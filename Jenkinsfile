pipeline {
    agent any

    environment {
        DOCKER_IMAGE = '2022bcs0050madhavmurali/mlops-lab'
        DOCKER_TAG = '${BUILD_NUMBER}'
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
                    // Initialize BEST_R2 and BEST_MSE with safer default values
                    env.BEST_R2 = "-100.0"
                    env.BEST_MSE = "100.0"
                    
                    // Default to false
                    env.SHOULD_PUBLISH = "false"
                    
                    try {
                        // Use separate try-catches to ensure one failure doesn't block the other
                        try {
                            withCredentials([string(credentialsId: 'best-r2-score', variable: 'STORED_BEST_R2')]) {
                                if (STORED_BEST_R2?.trim()) {
                                    env.BEST_R2 = STORED_BEST_R2
                                }
                            }
                        } catch (Exception e) {
                             echo "Credential 'best-r2-score' not found. Using default: -100.0"
                        }

                        try {
                            withCredentials([string(credentialsId: 'best-mse', variable: 'STORED_BEST_MSE')]) {
                                if (STORED_BEST_MSE?.trim()) {
                                    env.BEST_MSE = STORED_BEST_MSE
                                }
                            }
                        } catch (Exception e) {
                             echo "Credential 'best-mse' not found. Using default: 100.0"
                        }
                    } catch (Exception e) {
                        echo "Unexpected error loading credentials: ${e.getMessage()}"
                    }

                    echo "------------------------------------------------"
                    echo "Current Metrics: R2=${env.CURRENT_R2}, MSE=${env.CURRENT_MSE}"
                    echo "Best Stored Metrics: R2=${env.BEST_R2}, MSE=${env.BEST_MSE}"
                    echo "------------------------------------------------"

                    def currentR2 = env.CURRENT_R2.toFloat()
                    def bestR2 = env.BEST_R2.isNumber() ? env.BEST_R2.toFloat() : -100.0
                    
                    def currentMse = env.CURRENT_MSE.toFloat()
                    def bestMse = env.BEST_MSE.isNumber() ? env.BEST_MSE.toFloat() : 100.0

                    // Sanity Check: If Best R2 > 1.0, it's likely misconfigured (e.g. user entered MSE=100 into R2 field)
                    if (bestR2 > 1.0) {
                        echo "WARNING: Best R2 Score (${bestR2}) is > 1.0. This seems invalid for R2 Score."
                        echo "Make sure 'best-r2-score' credential is set correctly (e.g. -100.0, 0.0, or < 1.0)."
                    }

                    // For R2 Score, Higher is Better
                    if (currentR2 > bestR2) {
                        echo "SUCCESS: New model R2 Score (${currentR2}) is better (higher) than baseline (${bestR2})."
                        echo "New MSE: ${currentMse} (Baseline: ${bestMse})"
                        env.SHOULD_PUBLISH = "true"
                    } else {
                        echo "SKIP: New model R2 Score (${currentR2}) is not better than baseline (${bestR2})."
                        echo "New MSE: ${currentMse} (Baseline: ${bestMse})"
                        env.SHOULD_PUBLISH = "false"
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                expression { return env.SHOULD_PUBLISH == "true" }
            }
            steps {
                script {
                    echo "Building Docker image..."
                    dockerImage = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }

        stage('Push Docker Image') {
            when {
                expression { return env.SHOULD_PUBLISH == "true" }
            }
            steps {
                script {
                    echo "Pushing Docker image to Docker Hub..."
                    docker.withRegistry('', DOCKER_CREDENTIALS_ID) {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Archive artifacts regardless of success/failure
            archiveArtifacts artifacts: 'app/artifacts/**', fingerprint: true
            echo "Artifacts archived in 'app/artifacts/'"
        }
    }
}