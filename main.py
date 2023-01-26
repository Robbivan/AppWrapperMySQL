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
connection = mysql.connector.connect(user=data_gen['user'], password=data_gen['password'],
                                     host=data_gen['host'],
                                     database=data_gen['database'])

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


    def make_area_in(self): # создание области ввода
        f = Frame(self)
        self.f = f
        if ('select' in self.add_opt['is_input'] ):
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
            cursor = connection.cursor()

            columns = []

            cursor.execute(querry)
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
                cursor = connection.cursor()
                columns = []

                cursor.execute(querry)
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
        elif 'update' in self.add_opt['is_input']:
            querry_dop = self.add_opt['is_input']['update']
            entity = querry_dop['entity']
            fields = querry_dop['fields']
            fields_dop = querry_dop['fields_dop']

            self.checkboxes = querry_dop['checkboxes']
            lab = Label(f, text=querry_dop['label'])
            lab.pack(side=TOP)
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

            action_with_arg = partial(self.com_formated, self.command,
                                      self.entries, True)
            Button(f, text='Ввод', command=action_with_arg).pack(side=TOP)
        f.pack(side=LEFT)
    def execute(self, query_in): # выполнение запросов через cursor
        print(query_in)
        if (self.w_write):
            self.l_res.pack_forget()
            self.l_res.destroy()
            self.w_write = False
        columns = []
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
        print(columns)
        if len(all_rows) == 0:
            messagebox.showinfo("Порядок", "Ввод завершен успешно")
            self.w_write = False
            return
        self.w_write = True
        for i in cursor.description:
            columns.append(i[0])
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
    def com_formated(self, command, inputs, enten=False): # дефолтный обработчик
        if not enten:
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
        worker_action = partial(self.all_querrys, 'worker')
        button_for_worker = Button(self.chose_f,
                                   text='Сотрудник автосервиса',
                                   command=worker_action)
        button_for_worker.pack(side=RIGHT, fill=BOTH, expand=1)
        self.chose_f.pack(side=TOP, fill=BOTH, expand=1, anchor=CENTER)

        admin_action = partial(self.all_querrys, 'admin')
        button_for_admin = Button(self.chose_f,
                          text='Администратор',
                          command=admin_action)
        button_for_admin.pack(side=TOP, fill=BOTH, expand=1)
        client_action = partial(self.all_querrys, 'client')
        button_for_client = Button(self.chose_f,
                            text='Клиент',
                            command=client_action)
        button_for_client.pack(side=TOP, fill=BOTH, expand=1)



    def all_querrys(self, mode): # запросы
        self.chose_f.pack_forget()
        self.chose_f.destroy()
        if mode == 'admin': # для администратора
            login = 'admin'
            password = 'hardpass23'
            queries = {
                "Список услуг": {
                    'command':
                    "SELECT id AS 'id' ,title AS 'Услуга', price AS 'Цена' FROM services GROUP BY title, price;",
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
                "Информация о работе работника за период времени": {
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
                            'label':'Пожалуйста, выберите период и работника',
                            'entity':'workers',
                            'fields':
                                ['id','first_name', 'second_name', 'last_name'],
                            'checkboxes': (('день', 1), ('месяц', 30), ('квартал', 91), ('год', 365))
                        }
                    }
                },
                "Расчет стоимости услуг": {
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
                            'fields':['id','first_name', 'second_name', 'last_name'],
                            'checkboxes': (())
                        }
                    }
                },
                'Добавить работника': {
                    'command':
                    """INSERT INTO workers (first_name, second_name, last_name, telegram)
                        VALUES
                        ({}, {}, {}, {});""",
                    'is_input': {
                        'insert': {
                            'label':
                            'Пожалуйста, введите данные работник',
                            'entity':
                            'clients',
                            'fields': [['first_name', 'Имя сотрудника'], ['second_name', 'Фамилия'],['last_name', 'Отчество'], ['telegram', 'Телеграм']],
                            'checkboxes': (()),
                        }
                    }
                },
                'Добавить услугу': {
                    'command': """INSERT INTO services(var_id , title, price)
                        VALUES
                        ({}, {}, {});""",
                    'is_input': {
                        'insert': {
                            'label':
                            'Пожалуйста, введите название услуги',
                            'entity':
                            'services',
                            'fields': [['var_id', 'Id услуги'],['name', 'Название'], ['price','Цена']],
                            'checkboxes':(()),
                        }
                    }
                },
                'Добавить заказ для машин из базы данных': {
                    'command':
                        """INSERT INTO contracts(car_id, creation_date, end_date)
                            VALUES
                            ({}, {}, {});""",
                    'is_input': {
                        'insert': {
                            'label':
                                'Пожалуйста, введите данные заказа',
                            'entity': 'contracts',
                            'fields': [['creation_date', 'Дата создания'], ['final_date', 'Дата завершения'], ],
                            'checkboxes': ('cars', 'Машина', ['id', 'model_car', 'car_number'])
                        }
                    }
                },
                'Изменить расценки услуг': {
                    'command':
                        """UPDATE services SET price = {} WHERE id = {};""",
                    'is_input': {
                        'update': {
                            'label':
                                'Пожалуйста, введите данные',
                            'entity': 'services',
                            'fields': [['id', 'id услуги, у которой поменять цену'], ['price', 'Новая цена']],
                            'fields_dop': ['price'],
                            'checkboxes': (())
                        }
                    }
                },
                'Уточнить модель машины': {
                    'command':
                        """UPDATE cars SET model_car= {} WHERE car_number = {};""",
                    'is_input': {
                        'update': {
                            'label':
                                'Пожалуйста, введите данные',
                            'entity': 'services',
                            'fields': [['car_number', 'Номер машины'], ['model_car', 'Правильная модель']],
                            'fields_dop': ['model_car'],
                            'checkboxes': (())
                        }
                    }
                },
                'Изменить специализацию работника': {
                    'command':
                        """UPDATE spec_workers SET var_id = {} WHERE worker_id  = {};""",
                    'is_input': {
                        'update': {
                            'label':
                                'Пожалуйста, введите данные',
                            'entity': 'services',
                            'fields': [['worker_id', 'Id работника'], ['var_id', 'Id новой специализации']],
                            'fields_dop': ['var_id'],
                            'checkboxes': (())
                        }
                    }
                },
            }
        elif mode == 'client': # для клиента
            login = 'client'
            password = '' # для клиента пароль не нужен
            queries = {
                "Список услуг": {
                    'command':
                    "SELECT id AS 'id', title AS 'Услуга', price AS 'Цена' FROM services GROUP BY title, price;",
                    'is_input': False
                },
                "Расчет стоимости услуг": {
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
                            'fields':['id','first_name', 'second_name', 'last_name'],
                            'checkboxes': (())
                        }
                    }
                },


            }
        elif mode == 'worker':  # для работника автосервиса
            login = 'worker'
            password = 'bestwork'
            queries = {
                "Список услуг": {
                    'command':
                        "SELECT id AS 'id', title AS 'Услуга', price AS 'Цена' FROM services GROUP BY title, price;",
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
                "Информация о работе работник за период времени": {
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
                            'label': 'Пожалуйста, выберите период и работника',
                            'entity': 'workers',
                            'fields': ['id', 'first_name', 'second_name', 'last_name'],
                            'checkboxes': (('день', 1), ('месяц', 30), ('квартал', 90), ('год', 365))
                        }
                    }
                },
                "Расчет стоимости услуг": {
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
                            'fields': ['id','first_name', 'second_name', 'last_name'],
                            'checkboxes': (())
                        }
                    }
                },
                'Добавить заказ для машин из базы данных': {
                    'command':
                    """INSERT INTO contracts(car_id, creation_date, end_date)
                        VALUES
                        ({}, {}, {});""",
                    'is_input': {
                        'insert': {
                            'label':
                            'Пожалуйста, введите данные заказа',
                            'entity':'contracts',
                            'fields': [ ['creation_date', 'Дата создания'],['final_date', 'Дата завершения'],],
                            'checkboxes': ('cars', 'Машина', ['id', 'model_car', 'car_number'])
                        }
                    }
                },
                'Изменить расценки услуг': {
                    'command':
                        """UPDATE services SET price = {} WHERE id = {};""",
                    'is_input': {
                        'update': {
                            'label':
                                'Пожалуйста, введите данные',
                            'entity': 'services',
                            'fields': [['id','id услуги, у которой поменять цену'], ['price','Новая цена']],
                            'fields_dop':['price'],
                            'checkboxes': (())
                        }
                    }
                },
                'Уточнить модель машины': {
                    'command':
                        """UPDATE cars SET model_car= {} WHERE car_number = {};""",
                    'is_input': {
                        'update': {
                            'label':
                                'Пожалуйста, введите данные',
                            'entity': 'services',
                            'fields': [['car_number', 'Номер машины'], ['model_car', 'Правильная модель']],
                            'fields_dop': ['model_car'],
                            'checkboxes': (())
                        }
                    }
                },
            }
        f = Top_querry(self, link_db=NONE, queries=queries)  # объект инициализируемый
        f.pack(fill=BOTH, side=LEFT)


root = Tk()
root.title("Программа для автосервиса")



root.minsize(900, 400)
app = Main_application(root)
app.pack(fill=BOTH, expand=1)
root.mainloop()
