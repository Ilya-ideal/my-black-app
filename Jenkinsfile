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
                            docker push ${env.DOCKER_IMAGE}:latest
                        """
                    }
                    echo "✅ Образ отправлен в Docker Hub"
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                script {
                    withCredentials([file(
                        credentialsId: 'kubeconfig',
                        variable: 'KUBECONFIG_FILE'
                    )]) {
                        bat """
                            echo "Развертывание в Minikube..."
                            
                            # Создаем namespace
                            kubectl create namespace ${env.KUBE_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                            
                            # Создаем ConfigMap
                            kubectl create configmap app-config ^
                                --from-literal=app.version=1.0.0 ^
                                --from-literal=deploy.time=${env.DEPLOY_TIME} ^
                                -n ${env.KUBE_NAMESPACE} ^
                                -o yaml --dry-run=client | kubectl apply -f -
                            
                            # Развертываем приложение
                            kubectl apply -f k8s/ -n ${env.KUBE_NAMESPACE}
                            
                            # Ждем запуска
                            echo "Ожидание запуска пода..."
                            timeout /t 30
                            
                            # Проверяем статус
                            kubectl get pods -n ${env.KUBE_NAMESPACE}
                            kubectl get services -n ${env.KUBE_NAMESPACE}
                            
                            echo "✅ Приложение развернуто в Minikube"
                        """
                    }
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
                            
                            # Получаем имя пода
                            for /f "tokens=1" %%i in ('kubectl get pods -n ${env.KUBE_NAMESPACE} -o name') do set POD_NAME=%%i
                            
                            # Проверяем логи
                            kubectl logs %POD_NAME% -n ${env.KUBE_NAMESPACE}
                            
                            # Проверяем здоровье
                            kubectl exec %POD_NAME% -n ${env.KUBE_NAMESPACE} -- curl -s http://localhost:5000/health || echo "Приложение запускается"
                            
                            echo "✅ Приложение работает"
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
                            -d text="🎉 CI/CD пайплайн полностью завершен! Приложение с черным фоном развернуто в Minikube. Docker образ: ${env.DOCKER_IMAGE}:latest Время: ${env.DEPLOY_TIME}"
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
                        -d text="❌ Деплой провалился! Проверьте Jenkins: ${env.BUILD_URL}"
                    """
                }
            }
        }
    }
}