pipeline {
    agent any

    environment {
        IMAGE_NAME = "2022bcs0050madhavmurali/mlops-lab:latest"
        CONTAINER_NAME = "wine_test_container_2022bcs0050"
        PORT = "5051"
    }

    stages {

        stage('Pull Image') {
            steps {
                echo "=== 2022BCS0050 - Madhav Murali - Lab 7: Inference Validation ==="
                sh "docker pull ${IMAGE_NAME}"
            }
        }

        stage('Run Container') {
            steps {
                sh """
                docker rm -f ${CONTAINER_NAME} || true
                docker run -d -p ${PORT}:8000 --name ${CONTAINER_NAME} ${IMAGE_NAME}
                """
            }
        }

        stage('Wait for Service Readiness') {
            steps {
                script {
                    timeout(time: 90, unit: 'SECONDS') {
                        waitUntil {
                            def status = sh(
                                script: "curl -s -o /dev/null -w \"%{http_code}\" http://host.docker.internal:${PORT}/docs || true",
                                returnStdout: true
                            ).trim()

                            echo "Service status: ${status}"
                            return status == "200"
                        }
                    }
                }
            }
        }

        stage('Valid Inference Test') {
            steps {
                script {
                    echo "Student: Madhav Murali | Roll No: 2022BCS0050"
                    def response = sh(
                        script: """
                        curl -s -X POST http://host.docker.internal:${PORT}/predict \
                        -H "Content-Type: application/json" \
                        -d '{"fixed_acidity":7.4,
                             "volatile_acidity":0.7,
                             "citric_acid":0.0,
                             "residual_sugar":1.9,
                             "chlorides":0.076,
                             "free_sulfur_dioxide":11.0,
                             "total_sulfur_dioxide":34.0,
                             "density":0.9978,
                             "pH":3.51,
                             "sulphates":0.56,
                             "alcohol":9.4}'
                        """,
                        returnStdout: true
                    ).trim()

                    echo "Valid Response: ${response}"

                    if (!response.contains("wine_quality")) {
                        error("Prediction field missing in response")
                    }
                }
            }
        }

        stage('Invalid Inference Test') {
            steps {
                script {
                    echo "Student: Madhav Murali | Roll No: 2022BCS0050"
                    def status = sh(
                        script: """
                        curl -s -o /dev/null -w "%{http_code}" \
                        -X POST http://host.docker.internal:${PORT}/predict \
                        -H "Content-Type: application/json" \
                        -d '{"alcohol":10}'
                        """,
                        returnStdout: true
                    ).trim()

                    echo "Invalid Input HTTP Code: ${status}"

                    if (status == "200") {
                        error("Invalid input should not return 200")
                    }
                }
            }
        }

        stage('Stop Container') {
            steps {
                sh """
                docker stop ${CONTAINER_NAME} || true
                docker rm ${CONTAINER_NAME} || true
                """
            }
        }
    }

    post {
        success {
            echo "=== 2022BCS0050 - Madhav Murali - Inference validation PASSED ==="
        }
        failure {
            echo "=== 2022BCS0050 - Madhav Murali - Inference validation FAILED ==="
            sh "docker logs ${CONTAINER_NAME} || true"
        }
        always {
            sh "docker rm -f ${CONTAINER_NAME} || true"
        }
    }
}