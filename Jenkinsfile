pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'ilia2014a/my-black-app'
        KUBE_NAMESPACE = 'default'
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
                    // Убираем пробелы из времени
                    env.DEPLOY_TIME = new Date().format("yyyy-MM-dd-HH-mm-ss")
                    
                    bat """
                        echo "Сборка Docker образа..."
                        echo "Время сборки: ${env.DEPLOY_TIME}"
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
                            echo "Логин в Docker Hub..."
                            echo %DOCKER_PASSWORD% | docker login -u %DOCKER_USERNAME% --password-stdin
                            echo "Отправка образа в Docker Hub..."
                            docker push ${env.DOCKER_IMAGE}:latest
                        """
                    }
                    echo "✅ Образ отправлен в Docker Hub"
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    withCredentials([file(
                        credentialsId: 'kubeconfig',
                        variable: 'KUBECONFIG_FILE'
                    )]) {
                        bat """
                            echo "Развертывание в Kubernetes..."
                            kubectl create configmap app-config ^
                                --from-literal=app.version=1.0.0 ^
                                --from-literal=deploy.time=${env.DEPLOY_TIME} ^
                                -o yaml --dry-run=client | kubectl apply -f -
                            
                            kubectl apply -f k8s/
                            kubectl rollout status deployment/my-black-app --timeout=300s
                        """
                    }
                    echo "✅ Приложение развернуто в Kubernetes"
                }
            }
        }

        stage('Send Telegram Notification') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'telegram-bot-token', variable: 'TELEGRAM_BOT_TOKEN'),
                        string(credentialsId: 'telegram-chat-id', variable: 'TELEGRAM_CHAT_ID')
                    ]) {
                        def message = "✅ Деплой успешно завершен! Приложение с черным фоном запущено. Время: ${env.DEPLOY_TIME}"
                        
                        // Используем PowerShell для правильной кодировки
                        powershell """
                            `$token = "${TELEGRAM_BOT_TOKEN}"
                            `$chatId = "${TELEGRAM_CHAT_ID}"
                            `$text = "✅ Деплой успешно завершен! Приложение с черным фоном запущено. Время: ${env.DEPLOY_TIME}"
                            
                            `$body = @{
                                chat_id = `$chatId
                                text = `$text
                            }
                            
                            Invoke-RestMethod -Uri "https://api.telegram.org/bot`$token/sendMessage" `
                                -Method Post `
                                -ContentType "application/json; charset=utf-8" `
                                -Body (`$body | ConvertTo-Json)
                        """
                    }
                    echo "✅ Уведомление отправлено в Telegram"
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
                    // Английский текст чтобы избежать проблем с кодировкой
                    def message = "❌ Deployment failed! Check Jenkins: ${env.BUILD_URL}"
                    
                    powershell """
                        `$token = "${TELEGRAM_BOT_TOKEN}"
                        `$chatId = "${TELEGRAM_CHAT_ID}"
                        `$text = "❌ Deployment failed! Check Jenkins: ${env.BUILD_URL}"
                        
                        `$body = @{
                            chat_id = `$chatId
                            text = `$text
                        }
                        
                        Invoke-RestMethod -Uri "https://api.telegram.org/bot`$token/sendMessage" `
                            -Method Post `
                            -ContentType "application/json; charset=utf-8" `
                            -Body (`$body | ConvertTo-Json)
                    """
                }
            }
        }
    }
}