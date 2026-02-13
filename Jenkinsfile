pipeline {
    agent any

    environment {
        DOCKER_IMAGE = '2022bcs0050madhavmurali/mlops-lab'
        DOCKER_TAG = 'v12'
        DOCKER_CREDENTIALS_ID = '2022bcs0050-madhav-Docker'
        // We use an env variable for the flag
        SHOULD_PUBLISH = 'false' 
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup & Train') {
            steps {
                sh ''' 
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                python src/training.py
                mkdir -p app/artifacts
                cp models/metrics.json app/artifacts/
                cp models/model.pkl app/artifacts/
                '''
            }
        }
        
        stage('Read & Compare Accuracy') {
            steps {
                script {
                    // Get current metrics
                    def currentR2 = sh(script: "python3 -c 'import json; print(json.load(open(\"app/artifacts/metrics.json\"))[\"r2_score\"])'", returnStdout: true).trim().toFloat()
                    
                    // Default best R2
                    def bestR2 = -100.0
                    
                    try {
                        withCredentials([string(credentialsId: 'best-r2-score', variable: 'STORED_BEST_R2')]) {
                            if (STORED_BEST_R2) { bestR2 = STORED_BEST_R2.toFloat() }
                        }
                    } catch (Exception e) {
                        echo "No baseline found, using default."
                    }

                    echo "Comparing: Current ${currentR2} vs Best ${bestR2}"

                    if (currentR2 > bestR2) {
                        echo "Condition met. Setting SHOULD_PUBLISH to true."
                        env.SHOULD_PUBLISH = 'true'
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo "Starting Docker Build..."
                sh "docker build -t ${env.DOCKER_IMAGE}:${env.DOCKER_TAG} ."
                sh "docker tag ${env.DOCKER_IMAGE}:${env.DOCKER_TAG} ${env.DOCKER_IMAGE}:latest"
            }
        }

        stage('Push Docker Image') {

            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS_ID, usernameVariable: 'U', passwordVariable: 'P')]) {
                        sh "echo \$P | docker login -u \$U --password-stdin"
                        sh "docker push ${env.DOCKER_IMAGE}:${env.DOCKER_TAG}"
                        sh "docker push ${env.DOCKER_IMAGE}:latest"
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