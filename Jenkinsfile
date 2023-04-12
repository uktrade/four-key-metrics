pipeline {
    agent {
        docker {
            image 'python:3.10'
        }
    }
    stages {
        stage('version') {
            steps {
                sh 'python3 --version'
            }
        }
        stage('run') {
            steps {
                sh 'python3 scheduled_run.py'
            }
        }
    }
}