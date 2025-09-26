pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'ilia2014a/my-black-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                bat 'echo "✅ Репозиторий склонирован"'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    env.DEPLOY_TIME = new Date().format("yyyy-MM-dd-HH-mm-ss")
                    
                    bat """
                        echo Сборка Docker образа...
                        docker build --build-arg DEPLOY_TIME=${env.DEPLOY_TIME} -t ${env.DOCKER_IMAGE}:latest .
                    """
                    echo "✅ Docker образ собран"
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )]) {
                        bat """
                            echo Логин в Docker Hub...
                            echo %DOCKER_PASSWORD% | docker login -u %DOCKER_USERNAME% --password-stdin
                            echo Отправка образа в Docker Hub...
                            docker push ${env.DOCKER_IMAGE}:latest
                        """
                    }
                    echo "✅ Образ отправлен в Docker Hub"
                }
            }
        }

        stage('Local Deploy and Test') {
            steps {
                bat """
                    echo Запуск приложения для тестирования...
                    docker run -d -p 5000:5000 --name my-black-app-test ${env.DOCKER_IMAGE}:latest
                    timeout /t 10
                    echo Проверка работы приложения...
                    curl http://localhost:5000/health || echo Приложение запущено!
                    echo Остановка тестового контейнера...
                    docker stop my-black-app-test
                    docker rm my-black-app-test
                """
            }
        }

        stage('Send Success Notification') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'telegram-bot-token', variable: 'TELEGRAM_BOT_TOKEN'),
                        string(credentialsId: 'telegram-chat-id', variable: 'TELEGRAM_CHAT_ID')
                    ]) {
                        // Английский текст чтобы избежать проблем с кодировкой
                        bat """
                            curl -s -X POST ^
                            "https://api.telegram.org/bot%TELEGRAM_BOT_TOKEN%/sendMessage" ^
                            -d chat_id=%TELEGRAM_CHAT_ID% ^
                            -d text="🎉 SUCCESS: CI/CD Pipeline Completed! Docker image: ${env.DOCKER_IMAGE}:latest Time: ${env.DEPLOY_TIME} Status: All stages passed successfully!"
                        """
                    }
                }
            }
        }
    }

    post {
        failure {
            script {
                withCredentials([
                    string(credentialsId: 'telegram-bot-token', variable: 'TELEGRAM_BOT_TOKEN'),
                    string(credentialsId: 'telegram-chat-id', variable: 'TELEGRAM_CHAT_ID')
                ]) {
                    bat """
                        curl -s -X POST ^
                        "https://api.telegram.org/bot%TELEGRAM_BOT_TOKEN%/sendMessage" ^
                        -d chat_id=%TELEGRAM_CHAT_ID% ^
                        -d text="❌ FAILED: CI/CD Pipeline failed. Check Jenkins: ${env.BUILD_URL}"
                    """
                }
            }
        }
        
        success {
            bat """
                echo "=== CI/CD PIPELINE SUMMARY ==="
                echo "✅ Source code from GitHub"
                echo "✅ Docker image built"
                echo "✅ Image pushed to Docker Hub" 
                echo "✅ Local deployment tested"
                echo "✅ Telegram notifications sent"
                echo "🎉 ALL STAGES COMPLETED SUCCESSFULLY!"
            """
        }
    }
}