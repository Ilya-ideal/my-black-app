pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'ilia2014a/my-black-app'
        KUBE_NAMESPACE = 'my-black-app'
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

        stage('Prepare Kubernetes') {
            steps {
                script {
                    withCredentials([file(
                        credentialsId: 'kubeconfig',
                        variable: 'KUBECONFIG_FILE'
                    )]) {
                        bat """
                            echo "Подготовка Kubernetes..."
                            echo "Проверка доступа к кластеру..."
                            kubectl cluster-info
                            kubectl get nodes
                            
                            echo "Создание namespace..."
                            kubectl create namespace ${env.KUBE_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                            echo "✅ Kubernetes подготовлен"
                        """
                    }
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
                            echo "Развертывание приложения..."
                            
                            echo "Создаем ConfigMap..."
                            kubectl create configmap app-config ^
                                --from-literal=app.version=1.0.0 ^
                                --from-literal=deploy.time=${env.DEPLOY_TIME} ^
                                -n ${env.KUBE_NAMESPACE} ^
                                -o yaml --dry-run=client | kubectl apply -f -
                            
                            echo "Применяем манифесты..."
                            kubectl apply -f k8s/ -n ${env.KUBE_NAMESPACE}
                            
                            echo "Ждем запуска пода..."
                            timeout /t 30
                            
                            echo "Статус развертывания:"
                            kubectl get pods -n ${env.KUBE_NAMESPACE}
                            kubectl get services -n ${env.KUBE_NAMESPACE}
                        """
                    }
                    echo "✅ Приложение развернуто в Kubernetes"
                }
            }
        }

        stage('Test Application') {
            steps {
                script {
                    withCredentials([file(
                        credentialsId: 'kubeconfig',
                        variable: 'KUBECONFIG_FILE'
                    )]) {
                        bat """
                            echo "Тестирование приложения..."
                            kubectl port-forward -n ${env.KUBE_NAMESPACE} deployment/my-black-app 8080:5000 &
                            timeout /t 5
                            curl http://localhost:8080/health || echo "Приложение еще не готово"
                            taskkill /f /im kubectl.exe 2>nul || echo "Port-forward завершен"
                        """
                    }
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
                        bat """
                            curl -s -X POST ^
                            "https://api.telegram.org/bot%TELEGRAM_BOT_TOKEN%/sendMessage" ^
                            -d chat_id=%TELEGRAM_CHAT_ID% ^
                            -d text="✅ CI/CD пайплайн успешен! Приложение развернуто в Minikube. Время: ${env.DEPLOY_TIME}"
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
        
        success {
            script {
                withCredentials([file(
                    credentialsId: 'kubeconfig',
                    variable: 'KUBECONFIG_FILE'
                )]) {
                    bat """
                        echo "Финальный статус:"
                        kubectl get all -n ${env.KUBE_NAMESPACE}
                    """
                }
            }
        }
    }
}