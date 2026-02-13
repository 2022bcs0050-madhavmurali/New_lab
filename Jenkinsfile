def shouldPublish = false

pipeline {
    agent any

    environment {
        DOCKER_IMAGE = '2022bcs0050madhavmurali/mlops-lab'
        DOCKER_TAG = 'v12'
        DOCKER_CREDENTIALS_ID = '2022bcs0050-madhav-Docker'
        GITHUB_CREDENTIALS_ID = '2022bcs0050-madhav'
        // Global flag for publishing
        SHOULD_PUBLISH = 'false' 
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
                
                # Activate and install dependencies
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
                
                # Execute training script
                python src/training.py
                
                # Prepare artifacts directory required by Lab 6
                mkdir -p app/artifacts
                
                # Move generated artifacts from default 'models/' to 'app/artifacts/'
                cp models/metrics.json app/artifacts/
                cp models/model.pkl app/artifacts/
                '''
            }
        }
        
        stage ('Read Accuracy') {
            steps {
                script {
                    // Extract MSE (Mean Squared Error) using python
                    env.CURRENT_MSE = sh(
                        script: "python3 -c 'import json; print(json.load(open(\"app/artifacts/metrics.json\"))[\"mse\"])'",
                        returnStdout: true
                    ).trim()
                    
                    // Extract R2 Score
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
                    // Logic to compare metrics...
                    if (currentR2 > bestR2) {
                        echo "SUCCESS: New model is better."
                        env.SHOULD_PUBLISH = 'true'
                    } else {
                        env.SHOULD_PUBLISH = 'false'
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                expression { return shouldPublish }
            }
            steps {
                // Use SH to build. This BYPASSES the hudson.util.FormValidation error 
                // because Jenkins doesn't 'inspect' shell strings for Docker tags.
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
                    // We only use the plugin here to handle the 'docker login' credentials safely
                    docker.withRegistry('', DOCKER_CREDENTIALS_ID) {
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
        }
    }
}