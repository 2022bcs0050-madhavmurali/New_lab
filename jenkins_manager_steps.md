# Jenkins Manager Steps

Here are the steps to manage and run the Jenkins pipeline for this project.

## 1. Prerequisites

Ensure the following credentials are set up in Jenkins:

-   **Docker Hub Credentials**:
    -   **ID**: `2022bcs0050-madhav-Docker`
    -   **Type**: Username and Password
    -   **Description**: Docker Hub credentials for pushing images.

-   **GitHub Credentials** (if using private repo or pushing tags):
    -   **ID**: `2022bcs0050-madhav`
    -   **Type**: Username and Password (or Secret Text for PAT)
    -   **Description**: GitHub credentials for SCM checkout.

-   **Best R2 Score Tracker**:
    -   **ID**: `best-r2-score`
    -   **Type**: Secret Text
    -   **Description**: Stores the best R2 Score.
        -   Initialize with a **low value** (e.g., `-100.0` or `0.0`).
        -   **Note**: Higher R2 Score is better.

-   **Best MSE Tracker**:
    -   **ID**: `best-mse`
    -   **Type**: Secret Text
    -   **Description**: Stores the best Mean Squared Error.
        -   Initialize with a **high value** (e.g., `100.0`).
        -   **Note**: Lower MSE is better.

## 2. Pipeline Job Setup

1.  **Create a New Item**:
    -   Go to Jenkins Dashboard -> **New Item**.
    -   Enter a name (e.g., `mlops-lab-pipeline`).
    -   Select **Pipeline** or **Multibranch Pipeline**.
    -   Click **OK**.

2.  **Configure Pipeline**:
    -   Under the **Pipeline** section:
        -   **Definition**: `Pipeline script from SCM`.
        -   **SCM**: `Git`.
        -   **Repository URL**: `<your-repo-url>`.
        -   **Credentials**: Select `2022bcs0050-madhav`.
        -   **Branch Specifier**: `*/main` (or your working branch).
        -   **Script Path**: `Jenkinsfile` (or `Jenkinsfile.example`).
    -   Click **Save**.

## 3. Running the Pipeline

1.  Click **Build Now** on the left menu.
2.  Wait for the build to start.

## 4. Monitoring the Build

1.  Click on the build number (e.g., `#1`) in the Build History.
2.  Click **Console Output**.
3.  Look for the **Read Accuracy** stage to see the extracted metrics:
    -   **Jenkinsfile**: Displays both MSE and R2 Score.
    -   **Jenkinsfile.example**: Displays R2 Score.
4.  Look for the **Compare Accuracy** stage to see if the model improved:
    ```text
    SUCCESS: New model (...) is better than baseline (...).
    ```

## 5. Artifacts and Docker Image

-   **Artifacts**: If the build succeeds, artifacts (`metrics.json`, `model.pkl`) are archived and accessible from the build page under **Build Artifacts**.
-   **Docker Image**: If the model improves (is better than the stored best), a new Docker image will be built and pushed to Docker Hub with tags `${BUILD_NUMBER}` and `latest`.
