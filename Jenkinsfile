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
                echo "✅ Репозиторий склонирован"
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Устанавливаем время сборки
                    env.DEPLOY_TIME = new Date().format("yyyy-MM-dd HH:mm:ss")
                    
                    // Для Windows используем bat вместо sh
                    bat """
                        echo "Сборка Docker образа..."
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
                            docker login -u %DOCKER_USERNAME% -p %DOCKER_PASSWORD%
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
                        // Обновляем время деплоя в ConfigMap
                        bat """
                            echo "Развертывание в Kubernetes..."
                            kubectl create configmap app-config ^
                                --from-literal=app.version=1.0.0 ^
                                --from-literal=deploy.time=\"${env.DEPLOY_TIME}\" ^
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
                        
                        bat """
                            curl -s -X POST ^
                            "https://api.telegram.org/bot%TELEGRAM_BOT_TOKEN%/sendMessage" ^
                            -d chat_id=%TELEGRAM_CHAT_ID% ^
                            -d text="${message}"
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
                    def message = "❌ Деплой провалился! Проверьте Jenkins: ${env.BUILD_URL}"
                    
                    bat """
                        curl -s -X POST ^
                        "https://api.telegram.org/bot%TELEGRAM_BOT_TOKEN%/sendMessage" ^
                        -d chat_id=%TELEGRAM_CHAT_ID% ^
                        -d text="${message}"
                    """
                }
            }
        }
    }
}