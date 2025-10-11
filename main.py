import flet as ft
import sqlite3

class tarefas:
    def __init__(self, page: ft.Page):
        self.page = page
        
        # Configurações iniciais da janela
        self.page.bgcolor = ft.Colors.BLACK
        self.page.window_width = 350
        self.page.window_height = 450
        self.page.window_resizable = False
        self.page.window_always_on_top = True
        self.page.title = 'Tarefas'
        
        # Variáveis de estado
        self.task = ''
        self.view = 'all' # Estado de visualização: 'all', 'incomplete', 'complete'
        self.results = []
        
        # Inicialização do Banco de Dados
        self.db_execute('CREATE TABLE IF NOT EXISTS tasks(name TEXT, status TEXT)')
        
        # Primeira consulta para popular a lista inicial
        self.results = self.db_execute('SELECT name, status FROM tasks')
        
        # O Container principal que será atualizado
        self.tasks_container_instance = self.tasks_container()
        
        self.main_page()
        
    def db_execute(self, query, params = []):
        """Função genérica para executar comandos SQL e retornar resultados."""
        with sqlite3.connect('tarefas.db') as con:
            cur = con.cursor()
            cur.execute(query, params)
            con.commit()
            return cur.fetchall()

    # --- Métodos de Ação da Tarefa ---
    
    def task_action(self, e):
        """Controla a marcação/desmarcação de tarefas."""
        is_checked = e.control.value
        label = e.control.label
        
        new_status = 'complete' if is_checked else 'incomplete'
        
        # Atualiza o status no DB
        self.db_execute('UPDATE tasks SET status = ? WHERE name = ?', params=[new_status, label])

        # Recarrega os dados com base no filtro atual
        self._repopulate_results()

        self.update_tasks_list()

    def delete_task(self, e):
        """Exclui uma tarefa do DB e atualiza a UI."""
        # O botão de exclusão armazena o nome da tarefa na propriedade 'data'
        task_name = e.control.data
        
        # Exclui a tarefa do DB
        self.db_execute('DELETE FROM tasks WHERE name = ?', params=[task_name])
        
        # Recarrega os dados com base no filtro atual
        self._repopulate_results()
        
        # Atualiza a interface gráfica
        self.update_tasks_list()

    def _repopulate_results(self):
        """Função auxiliar para recarregar a lista de tarefas do DB conforme o filtro atual."""
        if self.view == 'all':
            self.results = self.db_execute('SELECT name, status FROM tasks')
        else:
            self.results = self.db_execute('SELECT name, status FROM tasks WHERE status = ?', params = [self.view])
        
    # --- UI Components ---

    def tasks_container(self):
        """Cria e retorna o Container com a lista de Checkboxes a partir de self.results."""
        
        controls_list = []
        for res in self.results:
            task_name = res[0]
            is_complete = res[1] == 'complete'
            
            controls_list.append(
                ft.Row(
                    [
                        ft.Checkbox(
                            label=task_name,
                            value=is_complete, 
                            on_change=self.task_action, # Chama a ação (marcar/desmarcar)
                            expand=True # Expande o checkbox para ocupar o espaço
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE,
                            icon_color = ft.Colors.RED_500,
                            data=task_name, # Armazena o nome da tarefa no botão para exclusão
                            on_click=self.delete_task # Chama o método de exclusão
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
            
        return ft.Container(
            height = self.page.height * 0.8,
            padding=10,
            content = ft.Column(
                controls = controls_list,
                scroll=ft.ScrollMode.ADAPTIVE
            )
        )
    
    # --- Métodos de Interação ---

    def set_value(self, e):
        """Atualiza a variável self.task com o valor do TextField."""
        self.task = e.control.value

    def add(self, e, input_task):
        """Adiciona uma nova tarefa ao DB e atualiza a UI."""
        name = self.task.strip()
        status = 'incomplete'

        if name:
            self.db_execute(query='INSERT INTO tasks (name, status) VALUES (?, ?)', params=[name, status])
            
            input_task.value = ''
            self.task = ''
            
            self._repopulate_results() # Recarrega a lista para mostrar o novo item
            
            self.update_tasks_list()

    def update_tasks_list(self):
        """Atualiza a interface gráfica com o novo estado de self.results."""
        new_tasks_container = self.tasks_container()
        
        # Atualiza o conteúdo do Container existente
        self.tasks_container_instance.content = new_tasks_container.content
        
        self.page.update()

    def tabs_changed(self, e):
        """Muda o filtro de tarefas exibidas com base na aba selecionada."""
        selected_index = e.control.selected_index
        
        if selected_index == 0:
            self.view = 'all'
        elif selected_index == 1:
            self.view = 'incomplete'
        elif selected_index == 2:
            self.view = 'complete'

        self._repopulate_results()
        self.update_tasks_list()
            
    def main_page(self):
        """Monta a estrutura principal da página."""
        
        input_task = ft.TextField(
            hint_text= 'Digite sua tarefa',
            expand=True,
            on_change=self.set_value)

        input_bar = ft.Row(
            controls=[
                input_task,
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    on_click=lambda e: self.add(e, input_task) 
                )
            ]
        )

        tabs = ft.Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[
                ft.Tab(text='Todos'),
                ft.Tab(text='Em andamento'),
                ft.Tab(text='Finalizados')
            ]
        ) 
        
        self.page.add(input_bar, tabs, self.tasks_container_instance)

ft.app (target= tarefas)
