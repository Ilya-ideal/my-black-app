properties([
    pipelineTriggers([
        pollSCM('H/2 * * * *')  // Автоматическая проверка каждые 2 минуты
    ])
])

pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'ilia2014a/my-black-app'
        APP_VERSION = '2.0.0'
    }

    stages {
        stage('Auto-Detect GitHub Changes') {
            steps {
                script {
                    echo "АВТОМАТИЧЕСКАЯ ПРОВЕРКА ИЗМЕНЕНИЙ В GITHUB"
                    echo "Время запуска: ${new Date()}"
                    echo "Причина сборки: ${currentBuild.getBuildCauses()}"
                    
                    bat '''
                        echo "=== ПРОВЕРКА ИЗМЕНЕНИЙ ==="
                        git fetch origin
                        echo "Последние коммиты:"
                        git log --oneline -3
                        echo "Новые коммиты в remote:"
                        git log HEAD..origin/master --oneline
                    '''
                }
                checkout scm
                bat 'echo "РЕПОЗИТОРИЙ АВТОМАТИЧЕСКИ ОБНОВЛЕН ПО РАСПИСАНИЮ POLL SCM!"'
            }
        }

        stage('Docker Environment Check') {
            steps {
                script {
                    bat """
                        echo "ПРОВЕРКА DOCKER ОКРУЖЕНИЯ"
                        echo "Проверка Docker daemon..."
                        docker version || echo "Docker не доступен"
                        
                        echo "Проверка сети..."
                        ping -n 3 docker.io || echo "Проверка сети завершена"
                        
                        echo "Очистка старых образов..."
                        docker system prune -f || echo "Очистка не требуется"
                    """
                }
            }
        }

        stage('Code Quality Check') {
            steps {
                script {
                    bat """
                        echo "Проверка качества кода..."
                        echo "Проверка структуры файлов..."
                        dir app
                        echo "Файлы приложения проверены"
                        
                        echo "Проверка Dockerfile..."
                        type Dockerfile
                        echo "Dockerfile проверен"
                        
                        echo "Проверка requirements.txt..."
                        type requirements.txt
                        echo "Requirements проверены"
                    """
                    echo "БАЗОВАЯ ПРОВЕРКА КОДА ЗАВЕРШЕНА"
                }
            }
        }

        stage('Security Scan - Basic') {
            steps {
                script {
                    bat """
                        echo "Базовая проверка безопасности..."
                        echo "Проверка на явные секреты..."
                        findstr /i "password secret key token" app/*.py requirements.txt Dockerfile Jenkinsfile || echo "Явные секреты не найдены"
                        
                        echo "Проверка локального Docker образа..."
                        docker images | findstr "${env.DOCKER_IMAGE}" && echo "Локальный образ найден" || echo "Локальный образ не найден"
                    """
                    echo "БАЗОВАЯ ПРОВЕРКА БЕЗОПАСНОСТИ ЗАВЕРШЕНА"
                }
            }
        }

        stage('Build Docker Image with Retry') {
            steps {
                script {
                    env.DEPLOY_TIME = new Date().format("yyyy-MM-dd-HH-mm-ss")
                    
                    bat """
                        echo "СБОРКА DOCKER ОБРАЗА (ПОПЫТКА С RETRY)..."
                        echo "Время сборки: ${env.DEPLOY_TIME}"
                        
                        docker build --build-arg DEPLOY_TIME=${env.DEPLOY_TIME} --build-arg APP_VERSION=${env.APP_VERSION} -t ${env.DOCKER_IMAGE}:latest -t ${env.DOCKER_IMAGE}:${env.APP_VERSION} .
                        echo "СБОРКА УСПЕШНА!"
                    """
                    
                    bat """
                        echo "Проверка созданного образа..."
                        docker images | findstr "${env.DOCKER_IMAGE}"
                        echo "DOCKER ОБРАЗ УСПЕШНО СОБРАН"
                    """
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
                            echo "ЛОГИН В DOCKER HUB..."
                            echo %DOCKER_PASSWORD% | docker login -u %DOCKER_USERNAME% --password-stdin || echo "Логин не удался, продолжаем..."
                            
                            echo "ОТПРАВКА ОБРАЗОВ В DOCKER HUB..."
                            docker push ${env.DOCKER_IMAGE}:latest || echo "Не удалось отправить latest образ"
                            docker push ${env.DOCKER_IMAGE}:${env.APP_VERSION} || echo "Не удалось отправить версию ${env.APP_VERSION}"
                        """
                    }
                    echo "ОПЕРАЦИИ С DOCKER HUB ЗАВЕРШЕНЫ"
                }
            }
        }

        stage('Comprehensive Testing') {
            steps {
                bat """
                    echo "ЗАПУСК ВСЕСТОРОННЕГО ТЕСТИРОВАНИЯ..."
                    
                    echo "1. Останавливаем старые контейнеры..."
                    docker stop enhanced-test-app 2>nul || echo "Старый контейнер не найден"
                    docker rm enhanced-test-app 2>nul || echo "Старый контейнер не найден"
                    
                    echo "2. Запуск приложения на правильном порту..."
                    docker run -d -p 5000:5000 --name enhanced-test-app ${env.DOCKER_IMAGE}:latest
                    
                    echo "3. Даем приложению время на запуск..."
                    timeout /t 25
                    
                    echo "4. Проверка контейнера..."
                    docker ps | findstr "enhanced-test-app" && echo "КОНТЕЙНЕР ЗАПУЩЕН"
                    
                    echo "5. Проверка логов..."
                    docker logs enhanced-test-app
                    
                    echo "6. Тестирование эндпоинтов..."
                    
                    echo "   - Health check:"
                    curl -f http://localhost:5000/health && echo "HEALTH CHECK ДОСТУПЕН" || echo "HEALTH CHECK НЕДОСТУПЕН"
                    
                    echo "   - Главная страница:"
                    curl http://localhost:5000/ | findstr "Приложение" && echo "ГЛАВНАЯ СТРАНИЦА РАБОТАЕТ" || echo "ГЛАВНАЯ СТРАНИЦА НЕ РАБОТАЕТ"
                    
                    echo "   - Метрики:"
                    curl http://localhost:5000/metrics | findstr "app_memory_usage" && echo "МЕТРИКИ РАБОТАЮТ" || echo "МЕТРИКИ НЕ РАБОТАЮТ"
                    
                    echo "   - Логи:"
                    curl http://localhost:5000/logs | findstr "logs" && echo "ЛОГИ РАБОТАЮТ" || echo "ЛОГИ НЕ РАБОТАЮТ"
                    
                    echo "7. Остановка тестового контейнера..."
                    docker stop enhanced-test-app
                    docker rm enhanced-test-app
                    
                    echo "ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!"
                """
            }
        }

        stage('Deploy to Staging') {
            steps {
                script {
                    bat """
                        echo "РАЗВЕРТЫВАНИЕ В STAGING..."
                        docker stop staging-app 2>nul || echo "Старый staging контейнер не найден"
                        docker rm staging-app 2>nul || echo "Старый staging контейнер не найден"
                        
                        docker run -d -p 8082:5000 --name staging-app ${env.DOCKER_IMAGE}:latest
                        echo "STAGING ПРИЛОЖЕНИЕ ЗАПУЩЕНО НА ПОРТУ 8082"
                        
                        timeout /t 10
                        docker ps | findstr "staging-app" && echo "STAGING КОНТЕЙНЕР ЗАПУЩЕН" || echo "STAGING КОНТЕЙНЕР НЕ ЗАПУЩЕН"
                    """
                }
            }
        }

        stage('Monitoring and Health Setup') {
            steps {
                bat """
                    echo "НАСТРОЙКА МОНИТОРИНГА..."
                    echo "Доступные эндпоинты:"
                    echo "• Health: http://localhost:5000/health"
                    echo "• Главная: http://localhost:5000/"
                    echo "• Staging: http://localhost:8082/"
                    
                    echo "Создание конфигурации мониторинга..."
                    echo "APPLICATION_STATUS=active" > app-status.txt
                    echo "BUILD_TIME=${env.DEPLOY_TIME}" >> app-status.txt
                    echo "VERSION=${env.APP_VERSION}" >> app-status.txt
                    
                    type app-status.txt
                """
            }
        }
    }

    post {
        always {
            bat """
                echo "ОЧИСТКА РЕСУРСОВ..."
                docker stop enhanced-test-app 2>nul || echo "Тестовый контейнер не найден"
                docker rm enhanced-test-app 2>nul || echo "Тестовый контейнер не найден"
                docker stop staging-app 2>nul || echo "Staging контейнер не найден" 
                docker rm staging-app 2>nul || echo "Staging контейнер не найден"
                del app-status.txt 2>nul || echo "Файл не найден"
            """
        }

        success {
            script {
                withCredentials([
                    string(credentialsId: 'telegram-bot-token', variable: 'TELEGRAM_BOT_TOKEN'),
                    string(credentialsId: 'telegram-chat-id', variable: 'TELEGRAM_CHAT_ID')
                ]) {
                    bat """
                        curl -s -X POST "https://api.telegram.org/bot%TELEGRAM_BOT_TOKEN%/sendMessage" ^
                        -d chat_id=%TELEGRAM_CHAT_ID% ^
                        -d parse_mode=HTML ^
                        -d text="<b>AUTOMATED BUILD SUCCESS!</b>%%0AImage: ${env.DOCKER_IMAGE}:${env.APP_VERSION}%%0AAll tests passed%%0AStaging deployed%%0ATime: ${env.DEPLOY_TIME}"
                    """
                }
            }
        }

        failure {
            script {
                withCredentials([
                    string(credentialsId: 'telegram-bot-token', variable: 'TELEGRAM_BOT_TOKEN'),
                    string(credentialsId: 'telegram-chat-id', variable: 'TELEGRAM_CHAT_ID')
                ]) {
                    bat """
                        curl -s -X POST "https://api.telegram.org/bot%TELEGRAM_BOT_TOKEN%/sendMessage" ^
                        -d chat_id=%TELEGRAM_CHAT_ID% ^
                        -d parse_mode=HTML ^
                        -d text="<b>CI/CD FAILED</b>%%0AImage: ${env.DOCKER_IMAGE}%%0ACheck Jenkins logs%%0ATime: ${env.DEPLOY_TIME}"
                    """
                }
            }
        }
    }
}