import pandas as pd
import psycopg2
from tkinter import *
from tkinter.ttk import *


class DBconvert:

    def __init__(self, dbname='', username='', pwd='', host='', port=''):

        self.dbname = dbname
        self.username = username
        self.pwd = pwd
        self.host = host
        self.port = port

        self.conn = psycopg2.connect(f"dbname = '{self.dbname}' user = '{self.username}' password = '{self.pwd}' host = '{self.host}' port = '{self.port}'")
        self.cur = self.conn.cursor()

    def list_tables(self):

        """
        Metodas grąžina visas vartotojo sukurtas lenteles duomenų bazėje
        """

        self.cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
        rows = self.cur.fetchall()
        tables = [i[0] for i in rows]
        return tables

    def fill_listbox(self):
        """
        metodas, kuris iteruoja tai ką gavo iš self.list.tables ir sukrauna į listbox langą

        """

        tables = self.list_tables()
        for table in tables:
            list1.insert(END, table)
        return(tables)

    def sql_df(self, table):
        """
        Metodas, kuris nuskaito lentelės turinį Postgre ir gražina pandas dataframe fromatu

        """
        df = pd.read_sql_query(f'SELECT * FROM {table}', self.conn)
        return df

    def df_excel(self, table):
        """
        Šitas ir trys žemiau esantys vykdo patį konvertavimą. Parametrą pasigauna iš atitinkamo mygtuko command, daugiau info mygtukų logikos aprašyme
        """

        df = self.sql_df(table)
        df.to_excel(f'{table}.xlsx')
        message.set(f"{table}.xlsx created!")
        print(f"{table}.xlsx created!")

    def df_csv(self, table):
        df = self.sql_df(table)
        df.to_csv(f'{table}.csv')
        message.set(f"{table}.csv created!")
        print(f"{table}.csv created!")

    def df_json(self, table):
        df = self.sql_df(table)
        df.to_json(f'{table}.json', force_ascii=False)
        message.set(f"{table}.json created!")
        print(f"{table}.json created!")

    def df_html(self, table):
        df = self.sql_df(table)
        df.to_html(f'{table}.html')
        message.set(f"{table}.html created!")
        print(f"{table}.html created!")

    def popupinfo(self):

        self.cur.execute(f"select pg_relation_size('{get_selected('')}')")
        size = int(self.cur.fetchall()[0][0]/1000)
        self.cur.execute(f"SELECT COUNT(*) FROM {get_selected('')}")
        rows = self.cur.fetchall()[0][0]
        self.cur.execute(f"SELECT COUNT (*) FROM information_schema.columns WHERE table_name='{get_selected('')}'")
        columns = self.cur.fetchall()[0][0]
        self.cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '{get_selected('')}'")
        ugly_names = self.cur.fetchall()
        names = ' | '.join([ugly_names[i][0] for i in range(len(ugly_names))])

        popup = Tk()
        popup.title("Info")
        popup.resizable(FALSE, FALSE)
        label = Label(popup, text=f'''
Table Name: {get_selected('')}
Size: {size} Kb
Number of Rows: {rows}
Number of Columns: {columns}
Column Names: 
{names}''')
        label.grid(row=0, column=0, pady=10, padx=10)
        b1 = Button(popup, text='OK', command=popup.destroy)
        b1.grid(row=1, column=0, pady=5, padx=5)

        popup.mainloop()

    def popuphelp(self):
        popup = Tk()
        popup.title("About")
        popup.resizable(FALSE, FALSE)
        label = Label(popup, text='''
    This simple tool connects to a PostgreSQL database, 
scans the tables in a 'public' schema  and converts them
to CSV, Excel, Json or HTML, creating a file in the same 
folder. The GUI is self-explanatory enough. If the connection
fails, most likely the connection credentials are wrong or
mistyped. This tool is created for learning purposes, and
will not have major implementations in future.  ''')
        label.grid(row=0, column=0, pady=10, padx=10)
        b1 = Button(popup, text='OK', command=popup.destroy)
        b1.grid(row=1, column=0, pady=5, padx=5)
        popup.mainloop()

    def close_connection(self):
        self.conn.close()
        window.destroy()
        print('Connection closed!')


def connect():
    """
    funkcija inicijuoja prisijungimą nuo mygtuko connect paspaudimo. Init Parametruose stringVar'ai (tai kas gautą įvedus info į laukelius)
    tuo pačiu, iš karto po prisijungimo užpildomas listboxas
    """
    try:
        db.__init__(dbname_entry.get(), username_entry.get(), psw_entry.get(),
                    host_entry.get(), int(port_entry.get()))
        list1.delete(0, END)
        db.fill_listbox()
        message.set(f"Connected to '{dbname_entry.get()}' DB")
    except:
        message.set(f'Connection failed!')


def get_selected(event):
    """
    funkcija suveikia paspaudus ant lentelės pavadinimo listbokse. Grąžina lentelės pavadinimą, kuris paskui naudojamas konvertavimo metoduose.
    """

    index = list1.curselection()
    tablelist = db.list_tables()
    print(tablelist[index[0]])
    return tablelist[index[0]]


window = Tk()
window.title("PSQL Table Converter")
window.resizable(FALSE, FALSE)

db = DBconvert()
tables = db.list_tables()
# print(tables)

l0 = Label(window, text='DB Name:')
l0.grid(row=0, column=0, sticky='e')

dbname_entry = StringVar()
e0 = Entry(window, textvariable=dbname_entry)
e0.grid(row=0, column=1)

l1= Label(window, text='Username:')
l1.grid(row=1, column=0, sticky='e')

username_entry = StringVar()
e1 = Entry(window, textvariable=username_entry)
e1.grid(row=1, column=1)

l2 = Label(window, text='Password:')
l2.grid(row=2, column=0, sticky='e')

psw_entry = StringVar()
e2 = Entry(window, show="*", textvariable=psw_entry)
e2.grid(row=2, column=1)

l3 = Label(window, text='Host:')
l3.grid(row=3, column=0, sticky='e')

host_entry = StringVar()
e3 = Entry(window, textvariable=host_entry)
e3.grid(row=3, column=1)

l4 = Label(window, text='Port:')
l4.grid(row=4, column=0, sticky='e')

port_entry = StringVar()
e4 = Entry(window, textvariable=port_entry)
e4.grid(row=4, column=1)

list1 = Listbox(window)
list1.grid(row=8, rowspan=6, column=0, padx=(5, 0))
list1.bind('<<ListboxSelect>>', get_selected)

b1 = Button(window, width=15, text='Connect', command=lambda: connect())
b1.grid(row=5, column=1, pady=5)

sep1 = Separator(window, orient='horizontal')
sep1.grid(row=6, column=0, columnspan=2, sticky='we', padx=5)

l5 = Label(window, text='Choose Table:')
l5.grid(row=7, column=0, pady=5, padx=5, sticky='w')

l6 = Label(window, text='Action:')
l6.grid(row=7, column=1, pady=5, padx=15, sticky='w')


# konvertavimo mygtukų logika :
# 1.lambda, nes be jos iš karto callins metodą.
# 2.metodas po lambdos vykdo konvertavimą.
# 3 metodo parametruose get_selected funkcija, kuri nurodo, su kuria lentele dirbti:
#   3.1 pasiima indeksą iš to, ką gražina list1.curselection()
#   3.2 įdeda jį į db.list_tables(), iš kur grįžta lentelės pavadinimas

b3 = Button(window, width=15, text='Table Info', command=lambda: db.popupinfo())
b3.grid(row=8, column=1)

b4 = Button(window, width=15, text='Convert to Excel', command=lambda: db.df_excel(get_selected(event='')))
b4.grid(row=9, column=1)

b5 = Button(window, width=15, text='Convert to CSV', command=lambda: db.df_csv(get_selected(event='')))
b5.grid(row=10, column=1)

b6 = Button(window, width=15, text='Convert to JSON', command=lambda: db.df_json(get_selected(event='')))
b6.grid(row=11, column=1)

b7 = Button(window, width=15, text='Convert to HTML', command=lambda: db.df_html(get_selected(event='')))
b7.grid(row=12, column=1)

b8 = Button(window, width=15, text='About', command=db.popuphelp)
b8.grid(row=13, column=1)

sep2 = Separator(window, orient='horizontal')
sep2.grid(row=14, column=0, columnspan=2, sticky='we', pady=5, padx=5)


message = StringVar()
status_label = Label(window, textvariable=message)
status_label.grid(row=15, column=0, columnspan=2)

window.protocol("WM_DELETE_WINDOW", db.close_connection)
window.mainloop()

