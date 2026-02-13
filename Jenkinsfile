pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    command: ["sleep"]
    args: ["9999999"]
"""
        }
    }
    
    environment {
        // 본인의 환경에 맞게 수정하세요
        DOCKER_IMAGE = "chaduri7913/my-python-app"
        INFRA_REPO_URL = "https://github.com/HyeonWooJo/my-infra-manifests"
        VERSION = "1.0.${BUILD_NUMBER}" // 빌드 번호를 태그로 사용
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Docker Build & Push with Kaniko') {
            steps {
                script {
                    // Jenkins UI에서 등록한 ID를 호출합니다.
                    // 변수명 DOCKER_HUB_USER, DOCKER_HUB_PASSWORD에 값이 할당됩니다.
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', 
                                                    passwordVariable: 'DOCKER_HUB_PASSWORD', 
                                                    usernameVariable: 'DOCKER_HUB_USER')]) {
                        container('kaniko') {
                            sh """
                            # Docker Hub 인증을 위한 config.json 생성
                            mkdir -p /kaniko/.docker
                            echo '{\"auths\":{\"https://index.docker.io/v1/\":{\"auth\":\"'\$(echo -n \$DOCKER_HUB_USER:\$DOCKER_HUB_PASSWORD | base64)'\"}}}' > /kaniko/.docker/config.json
                            
                            # Kaniko를 사용하여 이미지 빌드 및 푸시
                            /kaniko/executor \\
                                --context \$(pwd) \\
                                --dockerfile Dockerfile \\
                                --destination ${DOCKER_IMAGE}:${VERSION} \\
                                --destination ${DOCKER_IMAGE}:latest
                            """
                        }
                    }
                }
            }
        }

        stage('Update Manifest (GitOps)') {
            steps {
                // 1. 인프라 레포를 임시 폴더에 클론
                dir('infra-manifests') {
                    git url: "${INFRA_REPO_URL}", branch: 'main', credentialsId: 'github-token'
                    
                    // 2. sed 명령어로 values.yaml의 tag 부분을 현재 버전으로 수정
                    sh "sed -i 's/tag: .*/tag: \"${VERSION}\"/' helm-chart/values.yaml"
                    
                    // 3. 변경사항 푸시 (GitHub 토큰 사용)
                    withCredentials([usernamePassword(credentialsId: 'github-token', 
                                                    passwordVariable: 'GITHUB_TOKEN', 
                                                    usernameVariable: 'GITHUB_USER')]) {
                        sh """
                        git config user.email 'chaduri79134@gmail.com'
                        git config user.name 'HyeonWooJo'
                        git remote set-url origin https://\${GITHUB_USER}:\${GITHUB_TOKEN}@github.com/HyeonWooJo/my-infra-manifests.git
                        git fetch origin main
                        git pull --rebase origin main || true
                        git add .
                        git commit -m 'Update image tag to ${VERSION} [skip ci]' || true
                        git pull --rebase origin main || true
                        git push origin main || git push --force-with-lease origin main
                        """
                    }
                }
            }
        }
    }
}