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
                                -o yaml --dry-run=client | kubectl apply -f - --validate=false
                            
                            kubectl apply -f k8s/ --validate=false
                            timeout 30
                            kubectl get pods
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
                            -d text="✅ Деплой успешно завершен! Приложение с черным фоном запущено. Время: ${env.DEPLOY_TIME}"
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
                    bat """
                        curl -s -X POST ^
                        "https://api.telegram.org/bot%TELEGRAM_BOT_TOKEN%/sendMessage" ^
                        -d chat_id=%TELEGRAM_CHAT_ID% ^
                        -d text="❌ Деплой провалился! Проверьте Jenkins: ${env.BUILD_URL}"
                    """
                }
            }
        }
    }
}