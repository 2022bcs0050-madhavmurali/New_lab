pipeline {
    agent any

    environment {
        DOCKER_IMAGE = '2022bcs0050madhavmurali/mlops-lab'
        DOCKER_TAG = 'v12'
        DOCKER_CREDENTIALS_ID = '2022bcs0050-madhav-Docker'
    }
    
    stages {
        stage('Initial Check') {
            steps {
                echo "1. Current User: ${env.USER}"
                sh "docker --version"
            }
        }
        
        stage('Forced Docker Build and Push') {
            steps {
                script {
                    echo "2. Starting Build..."
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                    
                    echo "3. Starting Push..."
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDENTIALS_ID, usernameVariable: 'U', passwordVariable: 'P')]) {
                        sh "echo \$P | docker login -u \$U --password-stdin"
                        sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                        sh "docker push ${DOCKER_IMAGE}:latest"
                    }
                }
            }
        }
    }
}