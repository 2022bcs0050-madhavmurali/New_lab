pipeline {
    agent any

    environment {
        // Student Info - 2022BCS0050 Madhav Murali
        STUDENT_NAME   = "Madhav Murali"
        STUDENT_ID     = "2022BCS0050"

        // Docker config
        DOCKER_IMAGE   = "2022bcs0050madhavmurali/mlops-lab"
        DOCKER_TAG     = "latest"
        CONTAINER_NAME = "mlops-inference-${BUILD_NUMBER}"
        API_PORT       = "8765"
        API_URL        = "http://localhost:8765"

        // Timeouts
        STARTUP_TIMEOUT  = "60"   // seconds to wait for API readiness
    }

    stages {

        // ─────────────────────────────────────────────
        // Stage 1: Pull Image
        // ─────────────────────────────────────────────
        stage('Pull Image') {
            steps {
                echo "========================================"
                echo "  Lab 7 - Inference Validation"
                echo "  Student : ${env.STUDENT_NAME}"
                echo "  Roll No : ${env.STUDENT_ID}"
                echo "========================================"
                sh "docker pull ${env.DOCKER_IMAGE}:${env.DOCKER_TAG}"
                sh "docker image inspect ${env.DOCKER_IMAGE}:${env.DOCKER_TAG} --format='Image pulled successfully: {{.Id}}'"
            }
        }

        // ─────────────────────────────────────────────
        // Stage 2: Run Container
        // ─────────────────────────────────────────────
        stage('Run Container') {
            steps {
                sh """
                    docker run -d \
                        --name ${env.CONTAINER_NAME} \
                        -p ${env.API_PORT}:8000 \
                        ${env.DOCKER_IMAGE}:${env.DOCKER_TAG}
                    echo "Container ${env.CONTAINER_NAME} started on port ${env.API_PORT}"
                """
            }
        }

        // ─────────────────────────────────────────────
        // Stage 3: Wait for Service Readiness
        // ─────────────────────────────────────────────
        stage('Wait for Service Readiness') {
            steps {
                script {
                    def ready = false
                    def waited = 0
                    def interval = 3

                    echo "Waiting for API to be ready at ${env.API_URL} ..."
                    while (!ready && waited < env.STARTUP_TIMEOUT.toInteger()) {
                        def status = sh(
                            script: "curl -s -o /dev/null -w '%{http_code}' ${env.API_URL}/ || true",
                            returnStdout: true
                        ).trim()

                        if (status == "200") {
                            echo "API is ready! (HTTP ${status}) after ${waited}s"
                            ready = true
                        } else {
                            echo "API not ready yet (HTTP ${status}), waiting ${interval}s... [${waited}/${env.STARTUP_TIMEOUT}s]"
                            sleep(interval)
                            waited += interval
                        }
                    }

                    if (!ready) {
                        error("API did not become ready within ${env.STARTUP_TIMEOUT} seconds. Failing pipeline.")
                    }
                }
            }
        }

        // ─────────────────────────────────────────────
        // Stage 4: Send Valid Inference Request
        // ─────────────────────────────────────────────
        stage('Send Valid Inference Request') {
            steps {
                script {
                    echo "--- Sending VALID inference request ---"
                    echo "Student: ${env.STUDENT_NAME} | Roll No: ${env.STUDENT_ID}"

                    def validPayload = '''{
                        "fixed_acidity": 7.4,
                        "volatile_acidity": 0.7,
                        "citric_acid": 0.0,
                        "residual_sugar": 1.9,
                        "chlorides": 0.076,
                        "free_sulfur_dioxide": 11.0,
                        "total_sulfur_dioxide": 34.0,
                        "density": 0.9978,
                        "pH": 3.51,
                        "sulphates": 0.56,
                        "alcohol": 9.4
                    }'''

                    def response = sh(
                        script: """curl -s -w '\\nHTTP_STATUS:%{http_code}' \
                            -X POST '${env.API_URL}/predict' \
                            -H 'Content-Type: application/json' \
                            -d '${validPayload}'""",
                        returnStdout: true
                    ).trim()

                    // Split body and status code
                    def parts = response.split("HTTP_STATUS:")
                    def body   = parts[0].trim()
                    def httpCode = parts[1].trim()

                    echo "HTTP Status : ${httpCode}"
                    echo "Response    : ${body}"

                    // Validation 1: HTTP 200
                    if (httpCode != "200") {
                        error("VALIDATION FAILED: Expected HTTP 200, got ${httpCode}")
                    }
                    echo "✔ HTTP status is 200"

                    // Validation 2: prediction field exists
                    if (!body.contains("wine_quality")) {
                        error("VALIDATION FAILED: 'wine_quality' field not found in response")
                    }
                    echo "✔ 'wine_quality' field is present"

                    // Validation 3: value is numeric (extract and parse)
                    def matcher = body =~ /"wine_quality"\s*:\s*([\d.]+)/
                    if (!matcher) {
                        error("VALIDATION FAILED: Could not extract numeric wine_quality value from response")
                    }
                    def predValue = matcher[0][1].toFloat()
                    echo "✔ wine_quality value is numeric: ${predValue}"

                    // Validation 4: reasonable range (wine quality 0–10)
                    if (predValue < 0 || predValue > 10) {
                        error("VALIDATION FAILED: wine_quality=${predValue} is outside valid range [0, 10]")
                    }
                    echo "✔ wine_quality=${predValue} is within valid range [0, 10]"

                    echo ">>> VALID REQUEST TEST PASSED for ${env.STUDENT_ID} <<<"
                }
            }
        }

        // ─────────────────────────────────────────────
        // Stage 5: Send Invalid Request
        // ─────────────────────────────────────────────
        stage('Send Invalid Request') {
            steps {
                script {
                    echo "--- Sending INVALID (malformed) inference request ---"
                    echo "Student: ${env.STUDENT_NAME} | Roll No: ${env.STUDENT_ID}"

                    // Missing most required fields — should trigger a 422 Unprocessable Entity
                    def invalidPayload = '{"fixed_acidity": "not_a_number", "volatile_acidity": "bad"}'

                    def response = sh(
                        script: """curl -s -w '\\nHTTP_STATUS:%{http_code}' \
                            -X POST '${env.API_URL}/predict' \
                            -H 'Content-Type: application/json' \
                            -d '${invalidPayload}'""",
                        returnStdout: true
                    ).trim()

                    def parts    = response.split("HTTP_STATUS:")
                    def body     = parts[0].trim()
                    def httpCode = parts[1].trim()

                    echo "HTTP Status : ${httpCode}"
                    echo "Response    : ${body}"

                    // Validation: API must NOT return 200 for bad input
                    if (httpCode == "200") {
                        error("VALIDATION FAILED: API accepted malformed input with HTTP 200 — this is incorrect behaviour")
                    }
                    echo "✔ API correctly rejected malformed input (HTTP ${httpCode})"

                    // Validation: response must contain meaningful error info
                    if (!body.contains("detail") && !body.contains("error") && !body.contains("value_error")) {
                        error("VALIDATION FAILED: Error response does not contain meaningful error description")
                    }
                    echo "✔ Error response contains meaningful error description"

                    echo ">>> INVALID REQUEST TEST PASSED for ${env.STUDENT_ID} <<<"
                }
            }
        }

        // ─────────────────────────────────────────────
        // Stage 6: Stop Container
        // ─────────────────────────────────────────────
        stage('Stop Container') {
            steps {
                sh """
                    echo "Stopping container ${env.CONTAINER_NAME}..."
                    docker stop ${env.CONTAINER_NAME} || true
                    docker rm   ${env.CONTAINER_NAME} || true
                    echo "Container removed successfully."
                """
            }
        }

        // ─────────────────────────────────────────────
        // Stage 7: Pipeline Result
        // ─────────────────────────────────────────────
        stage('Pipeline Result') {
            steps {
                echo "========================================"
                echo "  ALL VALIDATION CHECKS PASSED"
                echo "  Student : ${env.STUDENT_NAME}"
                echo "  Roll No : ${env.STUDENT_ID}"
                echo "  PIPELINE STATUS: SUCCESS"
                echo "========================================"
            }
        }
    }

    // ─────────────────────────────────────────────
    // Post: always clean up the container, report status
    // ─────────────────────────────────────────────
    post {
        always {
            sh """
                docker stop ${env.CONTAINER_NAME} 2>/dev/null || true
                docker rm   ${env.CONTAINER_NAME} 2>/dev/null || true
            """
        }
        success {
            echo "========================================"
            echo "  PIPELINE PASSED - ${env.STUDENT_ID}"
            echo "  Student: ${env.STUDENT_NAME}"
            echo "========================================"
        }
        failure {
            echo "========================================"
            echo "  PIPELINE FAILED - ${env.STUDENT_ID}"
            echo "  Student: ${env.STUDENT_NAME}"
            echo "  Check console logs for details."
            echo "========================================"
        }
    }
}