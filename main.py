from functools import partial
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import mysql.connector


login = 'root'
password =''
# изначально ставится root, но затем через global меняется на права относительно заданных прав для БД
data_gen = {
    'host': "127.0.0.1",
    'user': login,
    'password': password,
    'database': "auto"
}

class Top_querry(ttk.Frame):
    def __init__(self, admin, *args, link_db, queries, **kwargs):
        super().__init__(admin, *args, **kwargs)
        self.link_db = link_db # задается связь для БД
        self.help_d = False
        self.admin = admin
        self.f_done = Frame(admin)
        l_f = Frame(self)
        for quer in queries.keys(): # Обрабатываются все запросы для текущего пользователя (клиент, администратор, сотрудник)
            option = queries[quer]
            argument = partial(self.make_text_info, option)
            r = Button(l_f, text=quer, command=argument)
            r.pack(side=TOP, fill=BOTH, expand=1)
        l_f.pack(side=TOP, fill=BOTH)


    def make_text_info(self, options): #создаются текстовые поля frame
        if self.help_d:
            self.w.pack_forget()
            self.w.destroy()

        self.w = Info_add_Text(self.admin,
                               link_db=self.link_db,
                               left_menu=self,
                               add_opt=options)
        self.w.pack(fill=BOTH, expand=1, side=RIGHT)
        self.help_d = True



class Info_add_Text(ttk.Frame): # обработка основных статических данных(текста), + вывод запросов
    def __init__(self, admin, link_db, *args, left_menu, add_opt, **kwargs):
        super().__init__(admin, *args, **kwargs)
        self.link_db = link_db
        self.add_opt = add_opt
        self.admin = admin
        self.command = add_opt['command']
        self.w_write = False
        if add_opt['is_input']:
            self.make_area_in()
        else:
            self.execute(self.add_opt['command'])

    def execute(self, query_in):
        print(query_in)
        if (self.w_write):
            self.l_res.pack_forget()
            self.l_res.destroy()
            self.w_write = False
        columns = []
        connection = mysql.connector.connect(user=data_gen['user'], password=data_gen['password'], host=data_gen['host'],
                                             database=data_gen['database'])
        cursor = connection.cursor()

        try:
            cursor.execute(query_in)
        except:
            messagebox.showinfo("Вероятная ошибка", "Проверьте данные")
            self.w_write = False
            return

        all_rows = cursor.fetchall()
        print(cursor.fetchall())

        for row in cursor.fetchall():
            print("::",row)

        for i in cursor.description:
            columns.append(i[0])
        print(columns)
        if len(columns) == 0:
            messagebox.showinfo("Порядок", "Ввод завершен успешно")
            self.w_write = False
            return
        self.w_write = True

        self.l_res = ttk.Treeview(self, show="headings")
        self.l_res['columns'] = columns
        for i in columns:
            self.l_res.column(i, anchor=CENTER)
            self.l_res.heading(i, text=i)
        ysb = Scrollbar(self, orient=VERTICAL, command=self.l_res.yview)
        self.l_res.configure(yscroll=ysb.set)
        for i in all_rows:
            self.l_res.insert("", END, values=i)

        self.l_res.pack(fill=BOTH, expand=1)


    def make_area_in(self):
        f = Frame(self)
        self.f = f
        if ('select' in self.add_opt['is_input']):
            querry_dop = self.add_opt['is_input']['select']
            entity = querry_dop['entity']
            fields = querry_dop['fields']
            self.checkboxes = querry_dop['checkboxes']
            lab = Label(f, text=querry_dop['label'])
            lab.pack(side=TOP)
            if self.checkboxes:
                com_fr = Frame(f)
                self.v = StringVar(com_fr, "1")
                for (text, val) in self.checkboxes:
                    Radiobutton(com_fr, text=text, variable=self.v,
                                value=val).pack(side=LEFT)
                com_fr.pack(side=TOP)
            querry_dop = ', '.join(fields)
            querry = "SELECT {} FROM {}".format(querry_dop, entity)
            connection = mysql.connector.connect(user=data_gen['user'], password=data_gen['password'], host=data_gen['host'],
                                                 database=data_gen['database'])
            cursor = connection.cursor()
            columns = []

            cursor.execute(querry) #НАШЕЛЛЛЛЛЛЛ
            all_rows = cursor.fetchall()

            for elem in all_rows:
                elem = list(map(str, elem))
                data = [elem[0]]
                action_with_arg = partial(self.com_formated, self.command, data)

                r = Button(f,text=' '.join(list(elem)),command=action_with_arg)
                r.pack(side=TOP, fill=BOTH, expand=1)

        elif 'insert' in self.add_opt['is_input']:
            querry_dop = self.add_opt['is_input']['insert']
            entity = querry_dop['entity']
            fields = querry_dop['fields']
            self.checkboxes = querry_dop['checkboxes']
            lab = Label(f, text=querry_dop['label'])
            lab.pack(side=TOP)
            if self.checkboxes:
                com_fr = Frame(f)
                l = Label(com_fr, text=self.checkboxes[1])
                l.pack(side=TOP)
                querry_dop = ', '.join(self.checkboxes[2])
                querry = "SELECT {} FROM {}".format(querry_dop,
                                                    self.checkboxes[0])

                connection = mysql.connector.connect(user=data_gen['user'], password=data_gen['password'],
                                                     host=data_gen['host'],
                                                     database=data_gen['database'])
                cursor = connection.cursor()
                columns = []

                cursor.execute(querry)  # НАШЕЛЛЛЛЛЛЛ
                all_rows = cursor.fetchall()
                self.v = StringVar(com_fr, "1")
                for row in all_rows:
                    row = list(map(str, row))
                    Radiobutton(com_fr,
                                text=' '.join(list(row)),
                                variable=self.v,
                                value=row[0]).pack(side=TOP)
                com_fr.pack(side=TOP)

            self.entries = []
            for (field, field_name) in fields:
                ent_f = Frame(f)
                l = Label(ent_f, text=field_name)
                l.pack(side=TOP)

                self.i = StringVar(ent_f, "")
                self.entries.append(self.i)
                entity = Entry(ent_f, textvariable=self.i)
                entity.pack(side=TOP)
                ent_f.pack(side=TOP)
            if self.checkboxes: self.entries.append(self.v)
            action_with_arg = partial(self.com_formated, self.command,
                                      self.entries, True)

            Button(f, text='Ввод', command=action_with_arg).pack(side=TOP)
        elif 'double_insert' in self.add_opt['is_input']:
            querry_dop = self.add_opt['is_input']['double_insert']
            entity = querry_dop['entity']
            self.checkboxes = querry_dop['checkboxes']
            self.entries = []
            cs_f = Frame(f)
            for box in self.checkboxes:

                com_fr = Frame(cs_f)
                querry = """SELECT {} 
                            FROM {}
                            ;""".format('®, '.join(box[1:]), box[0])
                connection = mysql.connector.connect(user=data_gen['user'], password=data_gen['password'],
                                                     host=data_gen['host'],
                                                     database=data_gen['database'])
                cursor = connection.cursor()
                columns = []

                cursor.execute(querry)  # НАШЕЛЛЛЛЛЛЛ
                all_rows = cursor.fetchall()
                self.c = StringVar(com_fr, "0")
                self.entries.append(self.c)
                for row in all_rows:
                    row = list(map(str, row))
                    Radiobutton(com_fr,
                                text=' '.join(list(row)),
                                variable=self.c,
                                value=row[0]).pack(side=TOP)
                com_fr.pack(side=LEFT)
            cs_f.pack(side=TOP)
            action_with_arg = partial(self.com_formated, self.command,
                                      self.entries, True)

            Button(f, text='Ввод', command=action_with_arg).pack(side=TOP)

        elif 'special_insert' in self.add_opt['is_input']:
            self.show = False
            com_fr = Frame(f)
            l = Label(com_fr, text='Заказы')
            l.pack(side=TOP)
            querry = """SELECT orders.id, cars.name, cars.car_number 
                        FROM orders, cars
                        WHERE orders.car_id = cars.id;"""
            connection = mysql.connector.connect(user=data_gen['user'], password=data_gen['password'],
                                                 host=data_gen['host'],
                                                 database=data_gen['database'])
            cursor = connection.cursor()
            columns = []

            cursor.execute(querry)  # НАШЕЛЛЛЛЛЛЛ
            all_rows = cursor.fetchall()
            self.o = StringVar(com_fr, "1")
            for row in all_rows:
                row = list(map(str, row))
                Radiobutton(com_fr,
                            text=' '.join(list(row)),
                            variable=self.o,
                            value=row[0]).pack(side=TOP)
            com_fr.pack(side=LEFT)
            com_fr = Frame(f)
            l = Label(com_fr, text='Услуги')
            l.pack(side=TOP)
            querry = """SELECT id, name, price 
                        FROM services
                    """

            connection = mysql.connector.connect(user=data_gen['user'], password=data_gen['password'],
                                                 host=data_gen['host'],
                                                 database=data_gen['database'])
            cursor = connection.cursor()
            columns = []

            cursor.execute(querry)
            all_rows = cursor.fetchall()
            self.s = StringVar(com_fr, "-1")
            self.m = ''
            for row in all_rows:
                row = list(map(str, row))
                Radiobutton(com_fr,
                            text=' '.join(list(row)),
                            variable=self.s,
                            value=row[0],
                            command=lambda: self.workers()).pack(side=TOP)
            com_fr.pack(side=LEFT)

        f.pack(side=LEFT)

    def workers(self): # вывод по работнику
        if self.show:
            self.c_f.pack_forget()
            self.c_f.destroy()

        self.show = True

        self.c_f = Frame(self.f)
        l = Label(self.c_f, text='Работники')
        l.pack(side=TOP)
        querry = """SELECT * FROM masters
                    WHERE id IN (SELECT master_id 
                        FROM types_masters 
                        WHERE type_id = (SELECT id 
								FROM services WHERE id = {}));
                    """.format(self.s.get())
        connection = mysql.connector.connect(user=data_gen['user'], password=data_gen['password'],
                                             host=data_gen['host'],
                                             database=data_gen['database'])
        cursor = connection.cursor()
        columns = []

        cursor.execute(querry)
        all_rows = cursor.fetchall()
        self.m = StringVar(self.c_f, "0")
        for row in all_rows:
            row = list(map(str, row))
            Radiobutton(self.c_f,
                        text=' '.join(list(row)),
                        variable=self.m,
                        value=row[0]).pack(side=TOP)
        self.entries = [self.o, self.s, self.m]
        action_with_arg = partial(self.com_formated, self.command,
                                  self.entries)

        self.b = Button(self.c_f, text='Ввод', command=action_with_arg).pack(
            fill=BOTH,
            expand=1,
            side=TOP,
        )
        self.c_f.pack(side=LEFT)

    def com_formated(self, command, inputs, ent=False): # дефолтный обработчик
        if 'special_insert' in self.add_opt[
                'is_input'] or 'double_insert' in self.add_opt['is_input']:
            self.inputs = inputs[:]

            f_command = command.format(*list(
                map(lambda x: "'" + x.get() + "'"
                    if x.get() != '' else 'NULL', self.inputs)))
            print(f_command)
        elif not ent:
            self.inputs = inputs[:]
            if self.checkboxes: self.inputs.append("'" + self.v.get() + "'")
            f_command = command.format(*self.inputs)
        else:
            self.inputs = inputs[:]
            f_command = command.format(*list(
                map(lambda x: "'" + x.get() + "'"
                    if x.get() != '' else 'NULL', self.inputs)))
            print(f_command)

        self.execute(f_command)




class Main_application(ttk.Frame):
    def __init__(self, master, *args, **kwargs):

        super().__init__(master, *args, **kwargs)

        self.master = master
        self.chose_f = Frame(self)

        admin_action = partial(self.all_querrys, 'admin')
        button_for_admin = Button(self.chose_f,
                          text='Администратор',
                          command=admin_action)
        button_for_admin.pack(side=TOP, fill=BOTH, expand=1)

        client_action = partial(self.all_querrys, 's_m')
        button_for_client = Button(self.chose_f,
                            text='Клиент',
                            command=client_action)
        button_for_client.pack(side=TOP, fill=BOTH, expand=1)

        worker_action = partial(self.all_querrys, 'c_m')
        button_for_worker = Button(self.chose_f,
                            text='Сотрудник автосервиса',
                            command=worker_action)
        button_for_worker.pack(side=TOP, fill=BOTH, expand=1)
        self.chose_f.pack(side=TOP, fill=BOTH, expand=1, anchor=CENTER)

    def all_querrys(self, mode):
        self.chose_f.pack_forget()
        self.chose_f.destroy()
        if mode == 'admin':
            login = 'root'
            password = ''
            queries = {
                "Список услуг": {
                    'command':
                    "SELECT title AS 'Услуга', price AS 'Цена' FROM services GROUP BY title, price;",
                    'is_input': False
                },
                "Список машин с их владельцами": {
                    'command': "SELECT cl.first_name AS 'Имя',cl.second_name AS 'Фамилия', model_car AS 'Модель машины', car_number AS 'Номер машины'  FROM cars  INNER JOIN clients AS cl ON cars.car_owner_id = cl.id",
                    'is_input': False
                },
                "Информация о машине (оказываемые услуги)": {
                    'command': """SELECT title AS 'Услуга',price AS 'Цена' FROM services
                                WHERE services.id IN (SELECT service_id FROM contract_services 
                                    WHERE contract_id IN (SELECT contracts.id FROM contracts
                                        WHERE  car_id = (SELECT cars.id FROM cars
                                                                WHERE cars.id = {})));""",
                    'is_input': {
                        'select': {
                            'label': 'Пожалуйста, выберите машину',
                            'entity': 'cars',
                            'fields': ['id', 'car_number', 'model_car'],
                            'checkboxes': (())
                        }
                    }
                },
                "Информация о работе мастера за период": {
                    'command':
                    """ SELECT contracts.id AS 'id заказа', services.title AS 'Название услуги', services.price AS 'Цена услуги', contracts.creation_date 
                    AS 'Дата начала контракта(заказа)', contracts.end_date AS 'Дата окончания контракта(заказа)'
                    FROM services, contracts, (SELECT service_id, contract_id 
						 FROM contract_services   
						 WHERE worker_id = (SELECT id 
						                    FROM workers
										    WHERE workers.id = {})
						) AS link_worker_service
                    WHERE services.id = link_worker_service.service_id
                    AND contracts.id = link_worker_service.contract_id AND  
                    contracts.end_date BETWEEN DATE_SUB(NOW(), INTERVAL {} DAY) AND NOW() ;""",
                    'is_input': {
                        'select': {
                            'label':'Пожалуйста, выберите период и мастера',
                            'entity':'workers',
                            'fields':['id','first_name', 'second_name', 'last_name'],
                            'checkboxes': (('день', 1), ('месяц', 30), ('квартал', 90), ('год', 365))
                        }
                    }
                },
                "Рассчет стоимости услуг": {
                    'command':
                    """SELECT  link_c_s.contract_id, link_c_s.car_number, SUM(services.price) as sum  
                                            FROM services, (SELECT contract_services.service_id, car_from_contract.contract_id, car_from_contract.car_number 
                                                            FROM contract_services , (SELECT contracts.id as contract_id, nes_cars.car_number 
                                                                                FROM contracts, (SELECT cars.id, cars.car_number  
                                                                                                FROM cars
                                                                                                WHERE cars.id IN (SELECT id 
                                                                                                                FROM cars 
                                                                                                                WHERE cars.car_owner_id IN (SELECT id 
                                                                                                                                    FROM clients
                                                                                                                                    WHERE clients.id = {}))
                                                                                            ) AS nes_cars
                                                                                WHERE contracts.car_id = nes_cars.id
                                                                                ) AS car_from_contract
                                                            WHERE car_from_contract.contract_id = contract_services.contract_id) AS link_c_s
                                                WHERE services.id = link_c_s.service_id
                                                GROUP BY link_c_s.contract_id;""",
                    'is_input': {
                        'select': {
                            'label': 'Пожалуйста, выберите клиента',
                            'entity': 'clients',
                            'fields':['first_name', 'second_name', 'last_name'],
                            'checkboxes': (())
                        }
                    }
                },
                'Добавить мастера': {
                    'command':
                    """INSERT INTO masters (name, second_name, last_name, phone_number)
                        VALUES
                        ({}, {}, {}, {});""",
                    'is_input': {
                        'insert': {
                            'label':
                            'Введите данные мастера',
                            'entity':
                            'clients',
                            'fields': [['name', 'имя'], ['second_name', 'фамилия'],
                                       ['last_name', 'отчество'],
                                       ['phone_number', 'номер телефона']],
                            'checkboxes': (()),
                        }
                    }
                },
                'Добавить заказ': {
                    'command':
                    """INSERT INTO orders (creation_date, final_date, car_id)
                        VALUES
                        ({}, {}, {});""",  #Даты без ковычек, подставить по ходу скрипта
                    'is_input': {
                        'insert': {
                            'label':
                            'Введите данные заказа',
                            'entity':
                            'orders',
                            'fields': [
                                ['creation_date', 'Дата создания'],
                                ['final_date', 'Дата завершения'],
                            ],
                            'checkboxes':
                            ('cars', 'машина', ['id', 'name', 'car_number'])
                        }
                    }
                },
                'Добавить машину': {
                    'command': """INSERT INTO cars (name, car_number, owner_id)
                        VALUES
                        ({}, {}, {});""",
                    'is_input': {
                        'insert': {
                            'label':
                            'Введите данные машины',
                            'entity':
                            'cars',
                            'fields': [
                                ['name', 'название машины'],
                                ['car_number', 'номер машины'],
                            ],
                            'checkboxes':
                            ('clients', 'клиент',
                             ['id', 'name', 'second_name', 'last_name'])
                        }
                    }
                },
                'Добавить клиента': {
                    'command':
                    """INSERT INTO clients (name, second_name, last_name, phone_number)
                        VALUES
                        ({}, {}, {}, {});""",
                    'is_input': {
                        'insert': {
                            'label':
                            'Введите данные клиента',
                            'entity':
                            'clients',
                            'fields': [['name', 'имя'],
                                       ['second_name', 'фамилия'],
                                       ['last_name', 'отчество'],
                                       ['phone_number', 'номер телефона']],
                            'checkboxes': (()),
                        }
                    }
                },
                'Добавить  тип услуги': {
                    'command': """INSERT INTO service_types (name)
                        VALUES
                        ({});""",
                    'is_input': {
                        'insert': {
                            'label': 'Введите название типа услуги',
                            'entity': 'service_types',
                            'fields': [
                                ['name', 'название'],
                            ],
                            'checkboxes': (()),
                        }
                    }
                },
                'Добавить мастеру тип услуги': {
                    'command': """
                        INSERT INTO types_masters (master_id, type_id)
                        VALUES
                        ({}, {});""",
                    'is_input': {
                        'double_insert': {
                            'label':
                            'Выберите название типа услуги и мастера',
                            'entity': ['types_masters'],
                            'checkboxes': (
                                ('services', 'id, name'),
                                ('masters', 'id', 'name', 'second_name',
                                 'last_name'),
                            ),
                        }
                    }
                },
                'Добавить услугу': {
                    'command': """INSERT INTO services (name, price, type_id)
                        VALUES
                        ({}, {}, {});""",
                    'is_input': {
                        'insert': {
                            'label':
                            'Введите название услуги',
                            'entity':
                            'services',
                            'fields': [['name', 'название'], ['price',
                                                              'цена']],
                            'checkboxes':
                            ('service_types', 'Типы услуг', ['id', 'name']),
                        }
                    }
                },
                'Добавить услугу к заказу': {
                    'command':
                    """INSERT INTO order_services (order_id, service_id, master_id)
                                    VALUES
                                        ({}, {}, {});""",
                    'is_input': {
                        'special_insert': {
                            'label':
                            'Введите название услуги',
                            'entity':
                            'services',
                            'radiobuttons': (
                                ('orders', 'Заказы', ['id']),
                                ('services', 'Услуги', ['id', 'name',
                                                        'price']),
                                ('masters', 'Мастер',
                                 ['id', 'name', 'second_name', 'last_name']),
                            )
                        }
                    }
                },
            }
        elif mode == 's_m':
            login = 'staff_manager'
            password = 'staff_manager'
            queries = {
                "Список услуг": {
                    'command':
                    "SELECT name, price FROM services GROUP BY name, price;",
                    'is_input': False
                },
                'Добавить мастера': {
                    'command':
                    """INSERT INTO masters (name, second_name, last_name, phone_number)
                        VALUES
                        ({}, {}, {}, {});""",
                    'is_input': {
                        'insert': {
                            'label':
                            'Введите данные мастера',
                            'entity':
                            'clients',
                            'fields': [['name', 'имя'],
                                       ['second_name', 'фамилия'],
                                       ['last_name', 'отчество'],
                                       ['phone_number', 'номер телефона']],
                            'checkboxes': (()),
                        }
                    }
                },
                "Информация о работе мастера за период": {
                    'command':
                    """ SELECT orders.id, services.name, services.price, orders.creation_date, orders.final_date
                    FROM services, orders, (SELECT service_id, order_id 
						 FROM order_services  
						WHERE master_id = (SELECT id 
										   FROM masters
										    WHERE masters.id = {})
						) AS cur_s_o
                    WHERE services.id = cur_s_o.service_id
                    AND
                    orders.id = cur_s_o.order_id
                    AND 
                    orders.final_date IS NOT NULL
                    AND 
                    orders.final_date BETWEEN DATE_SUB(NOW(), INTERVAL {} DAY) AND NOW() ;""",
                    'is_input': {
                        'select': {
                            'label':
                            'Выберите период и мастера',
                            'entity':
                            'masters',
                            'fields':
                            ['id', 'name', 'second_name', 'last_name'],
                            'checkboxes': (('день', 1), ('месяц', 30),
                                           ('квартал', 91), ('год', 365))
                        }
                    }
                },
                'Добавить мастеру тип услуги': {
                    'command': """
                        INSERT INTO types_masters (master_id, type_id)
                        VALUES
                        ({}, {});""",
                    'is_input': {
                        'double_insert': {
                            'label':
                            'Выберите название типа услуги и мастера',
                            'entity': ['types_masters'],
                            'checkboxes': (
                                ('services', 'id, name'),
                                ('masters', 'id', 'name', 'second_name',
                                 'last_name'),
                            ),
                        }
                    }
                },
            }
        elif mode == 'c_m':
            login = 'client_manager'
            password = 'client_manager'
            queries = {
                "Список услуг": {
                    'command':
                    "SELECT name, price FROM services GROUP BY name, price;",
                    'is_input': False
                },
                "Список машин": {
                    'command': "SELECT * FROM cars;",
                    'is_input': False
                },
                "Информация о машине": {
                    'command': """SELECT * FROM services
                                WHERE id IN	(SELECT service_id FROM order_services
                                    WHERE order_id IN (SELECT id FROM orders
                                        WHERE  car_id = (SELECT id FROM cars
                                                                WHERE id = {})));""",
                    'is_input': {
                        'select': {
                            'label': 'Выберите машину',
                            'entity': 'cars',
                            'fields': ['id', 'name', 'car_number'],
                            'checkboxes': (())
                        }
                    }
                },
                "Рассчет стоимости услуг": {
                    'command':
                    """SELECT  o_c_s.order_id, o_c_s.car_number, SUM(services.price) as sum  
                                            FROM services, (SELECT order_services.service_id, order_car.order_id, order_car.name, order_car.car_number 
                                                            FROM order_services, (SELECT orders.id as order_id , selected_cars.name, selected_cars.car_number 
                                                                                FROM orders, (SELECT  cars.id, cars.name, cars.car_number  
                                                                                                FROM cars
                                                                                                WHERE cars.id IN (SELECT id 
                                                                                                                FROM cars 
                                                                                                                WHERE owner_id IN (SELECT id 
                                                                                                                                    FROM clients
                                                                                                                                    WHERE clients.id = {}))
                                                                                            ) AS selected_cars
                                                                                WHERE orders.car_id = selected_cars.id
                                                                                ) AS order_car
                                                            WHERE order_car.order_id = order_services.order_id) AS o_c_s
                                                WHERE services.id = o_c_s.service_id
                                                GROUP BY o_c_s.order_id;""",
                    'is_input': {
                        'select': {
                            'label': 'Выберите клиента',
                            'entity': 'clients',
                            'fields':
                            ['id', 'name', 'second_name', 'last_name'],
                            'checkboxes': (())
                        }
                    }
                },
                'Добавить заказ': {
                    'command':
                    """INSERT INTO orders (creation_date, final_date, car_id)
                        VALUES
                        ({}, {}, {});""",  #Даты без ковычек, подставить по ходу скрипта
                    'is_input': {
                        'insert': {
                            'label':
                            'Введите данные заказа',
                            'entity':
                            'orders',
                            'fields': [
                                ['creation_date', 'Дата создания'],
                                ['final_date', 'Дата завершения'],
                            ],
                            'checkboxes':
                            ('cars', 'машина', ['id', 'name', 'car_number'])
                        }
                    }
                },
                'Добавить машину': {
                    'command': """INSERT INTO cars (name, car_number, owner_id)
                        VALUES
                        ({}, {}, {});""",
                    'is_input': {
                        'insert': {
                            'label':
                            'Введите данные машины',
                            'entity':
                            'cars',
                            'fields': [
                                ['name', 'название машины'],
                                ['car_number', 'номер машины'],
                            ],
                            'checkboxes':
                            ('clients', 'клиент',
                             ['id', 'name', 'second_name', 'last_name'])
                        }
                    }
                },
                'Добавить клиента': {
                    'command':
                    """INSERT INTO clients (name, second_name, last_name, phone_number)
                        VALUES
                        ({}, {}, {}, {});""",
                    'is_input': {
                        'insert': {
                            'label':
                            'Введите данные клиента',
                            'entity':
                            'clients',
                            'fields': [['name', 'имя'],
                                       ['second_name', 'фамилия'],
                                       ['last_name', 'отчество'],
                                       ['phone_number', 'номер телефона']],
                            'checkboxes': (()),
                        }
                    }
                },
                'Добавить услугу к заказу': {
                    'command':
                    """INSERT INTO order_services (order_id, service_id, master_id)
                                    VALUES
                                        ({}, {}, {});""",
                    'is_input': {
                        'special_insert': {
                            'label':
                            'Введите название услуги',
                            'entity':
                            'services',
                            'radiobuttons': (
                                ('orders', 'Заказы', ['id']),
                                ('services', 'Услуги', ['id', 'name',
                                                        'price']),
                                ('masters', 'Мастер',
                                 ['id', 'name', 'second_name', 'last_name']),
                            )
                        }
                    }
                },
            }

        try:
            f = Top_querry(self, link_db=NONE, queries=queries)  # объект инициализируемый
            f.pack(fill=BOTH, side=LEFT)
        except 1210:
            print("ProgrammingError")
        except "33":
            print("invalid SQL descriptor name")




root = Tk()
root.title("Программа для автосервис")

root.minsize(900, 400)
app = Main_application(root)
app.pack(fill=BOTH, expand=1)
root.mainloop()
