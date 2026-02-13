def shouldPublish = false

pipeline {
    agent any

    environment {
        DOCKER_IMAGE = '2022bcs0050madhavmurali/mlops-lab'
        DOCKER_TAG = 'v12'
        DOCKER_CREDENTIALS_ID = '2022bcs0050-madhav-Docker'
        GITHUB_CREDENTIALS_ID = '2022bcs0050-madhav'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python Virtual Environment') {
            steps {
                sh ''' 
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }
        
        stage('Train Model') {
            steps {
                sh '''
                . venv/bin/activate
                python src/training.py
                mkdir -p app/artifacts
                cp models/metrics.json app/artifacts/
                cp models/model.pkl app/artifacts/
                '''
            }
        }
        
        stage('Read Accuracy') {
            steps {
                script {
                    env.CURRENT_MSE = sh(
                        script: "python3 -c 'import json; print(json.load(open(\"app/artifacts/metrics.json\"))[\"mse\"])'",
                        returnStdout: true
                    ).trim()
                    
                    env.CURRENT_R2 = sh(
                        script: "python3 -c 'import json; print(json.load(open(\"app/artifacts/metrics.json\"))[\"r2_score\"])'",
                        returnStdout: true
                    ).trim()
                    
                    echo "Current MSE: ${env.CURRENT_MSE}"
                    echo "Current R2 Score: ${env.CURRENT_R2}"
                }
            }
        }
        
        stage('Compare Accuracy') {
            steps {
                script {
                    // Initialize defaults
                    def bestR2 = -100.0
                    
                    // Try to fetch the best R2 from Jenkins Credentials
                    try {
                        withCredentials([string(credentialsId: 'best-r2-score', variable: 'STORED_BEST_R2')]) {
                            if (STORED_BEST_R2?.trim()) {
                                bestR2 = STORED_BEST_R2.toFloat()
                            }
                        }
                    } catch (Exception e) {
                        echo "Credential 'best-r2-score' not found. Using default: -100.0"
                    }

                    def currentR2 = env.CURRENT_R2.toFloat()

                    echo "------------------------------------------------"
                    echo "Comparison: Current R2 (${currentR2}) vs Best R2 (${bestR2})"
                    echo "------------------------------------------------"

                    if (currentR2 > bestR2) {
                        echo "SUCCESS: New model is better."
                        shouldPublish = true
                    } else {
                        echo "SKIP: New model is not better."
                        shouldPublish = false
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                expression { return shouldPublish }
            }
            steps {
                // BYPASSING Jenkins Docker Plugin Validation by using raw shell
                sh "docker build -t ${env.DOCKER_IMAGE}:${env.DOCKER_TAG} ."
                sh "docker tag ${env.DOCKER_IMAGE}:${env.DOCKER_TAG} ${env.DOCKER_IMAGE}:latest"
            }
        }

        stage('Push Docker Image') {
            when {
                expression { return shouldPublish }
            }
            steps {
                script {
                    // Force the registry URL to Docker Hub's official endpoint
                    docker.withRegistry('https://registry.hub.docker.com', DOCKER_CREDENTIALS_ID) {
                        // Use env. variables to ensure we are pushing exactly what we built
                        sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                        sh "docker push ${DOCKER_IMAGE}:latest"
                    }
                }
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'app/artifacts/**', fingerprint: true
            echo "Artifacts archived in 'app/artifacts/'"
        }
    }
}