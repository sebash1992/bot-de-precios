import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor 
from config import DB_HOST, DB_NAME, DB_USER, DB_PASS

class Database:
    def __init__(self):
        self.conn = None

    def connect_to_db(self):
        """Conecta a la base de datos PostgreSQL."""
        try:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            print("Conexión exitosa a la base de datos.")
        except psycopg2.DatabaseError as e:
            print(f"Error al conectar con la base de datos: {e}")
            self.conn = None

    def insert_record(self, table_name, column_values):
        """
        Inserta un registro en una tabla especificada.
        
        :param table_name: Nombre de la tabla.
        :param column_values: Diccionario con nombres de columnas como claves y valores a insertar como valores.
        """
        if self.conn is None:
            print("La conexión a la base de datos no está establecida.")
            return

        try:
            cursor = self.conn.cursor()
            columns = sql.SQL(', ').join(map(sql.Identifier, column_values.keys()))
            values = sql.SQL(', ').join(sql.Placeholder() * len(column_values))
            query = sql.SQL("INSERT INTO {table} ({columns}) VALUES ({values})").format(
                table=sql.Identifier(table_name),
                columns=columns,
                values=values
            )
            cursor.execute(query, list(column_values.values()))
            self.conn.commit()
            print("Registro insertado exitosamente.")
        except psycopg2.Error as e:
            print(f"Error al insertar el registro: {e}")
            self.conn.rollback()
        finally:
            cursor.close()

    def select_records(self, table_name, columns='*', condition=None):
        """
        Selecciona registros de una tabla especificada.
        
        :param table_name: Nombre de la tabla.
        :param columns: Columnas a seleccionar, por defecto todas.
        :param condition: Condición opcional para filtrar los registros.
        :return: Lista de registros.
        """
        if self.conn is None:
            print("La conexión a la base de datos no está establecida.")
            return []

        try:
            cursor = self.conn.cursor()
            query = sql.SQL("SELECT {fields} FROM {table}").format(
                fields=sql.SQL(', ').join(map(sql.Identifier, columns)) if columns != '*' else sql.SQL('*'),
                table=sql.Identifier(table_name)
            )

            if condition:
                query += sql.SQL(" WHERE {condition}").format(condition=sql.SQL(condition))
                
            cursor.execute(query)
            records = cursor.fetchall()
            return records
        except psycopg2.Error as e:
            print(f"Error al seleccionar los registros: {e}")
            return []
        finally:
            cursor.close()

    def select_records(self, table_name, columns='*', condition=None, condition_params=None):
        """
        Selecciona registros de una tabla especificada.
        
        :param table_name: Nombre de la tabla.
        :param columns: Columnas a seleccionar, por defecto todas.
        :param condition: Condición opcional para filtrar los registros.
        :param condition_params: Parámetros para la condición, si se proporcionan.
        :return: Lista de registros.
        """
        if self.conn is None:
            print("La conexión a la base de datos no está establecida.")
            return []

        try:
            cursor = self.conn.cursor()

            # Crear la consulta SQL dinámica
            query = sql.SQL("SELECT {fields} FROM {table}").format(
                fields=sql.SQL(', ').join(map(sql.Identifier, columns)) if columns != '*' else sql.SQL('*'),
                table=sql.Identifier(table_name)
            )

            # Agregar condición si existe
            if condition:
                query += sql.SQL(" WHERE {condition}").format(condition=sql.SQL(condition))
                
            # Ejecutar la consulta con parámetros seguros
            cursor.execute(query, condition_params)
            records = cursor.fetchall()
            return records
        except psycopg2.Error as e:
            print(f"Error al seleccionar los registros: {e}")
            return []
        finally:
            cursor.close()

    def execute_query(self, query, params=None):
        """
        Ejecuta una consulta SQL pasada como cadena.
        
        :param query: La consulta SQL a ejecutar.
        :param params: Una tupla de parámetros para la consulta (opcional).
        :return: Lista de registros si la consulta devuelve resultados, None si es una consulta de acción.
        """
        if self.conn is None:
            print("La conexión a la base de datos no está establecida.")
            return None

        try:
            # Usar DictCursor para que los resultados se devuelvan como diccionarios
            cursor = self.conn.cursor(cursor_factory=DictCursor)
            cursor.execute(query, params)
            if cursor.description:
                records = cursor.fetchall()
                return records
            else:
                self.conn.commit()
                print("Consulta ejecutada exitosamente.")
        except psycopg2.Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            self.conn.rollback()
        finally:
            cursor.close()

    def update_record(self, query, params):
        if self.connection is None:
            print("No hay conexión a la base de datos.")
            return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
                print("Actualización exitosa.")
        except Exception as e:
            print(f"Error al actualizar el registro: {e}")
            self.connection.rollback()

    def close_connection(self):
        """Cierra la conexión a la base de datos."""
        if self.conn is not None:
            self.conn.close()
            print("Conexión cerrada.")
