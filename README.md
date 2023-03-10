# QKD на базе SimulaQron

Фреймворк для моделирования распределения квантового ключа
(КРК, [QKD](https://en.wikipedia.org/wiki/Quantum_key_distribution)) в сети
квантовых коммуникаций согласно алгоритму [BB84](https://ru.wikipedia.org/wiki/BB84).

Коммуникация построена по принципу клиент-серверного взаимодействия
на бэкенде [SimulaQron](http://www.simulaqron.org/).

Включает коррекцию ошибок битов ключа по протоколу [Cascade](https://arxiv.org/pdf/1407.3257.pdf).

# Запуск

1. Установить зависимости 
  <pre><code>pip install -r requirements.txt</code></pre>

2. Перейти в папку эксперимента.

3. Запустить `network_start.py` в отдельном процессе.

4. Выполнить `run_nodes.sh`, запускающий скрипты узлов в отдельных процессах.

# Авторы

* [Пётр Шевченко](https://github.com/MorrisNein), 

* [Валерий Беляков](https://github.com/VabeNIZ).
