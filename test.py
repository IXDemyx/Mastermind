from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import random
import mastermind_cmd
from kivy.uix.screenmanager import ScreenManager, Screen
import json
from kivy.uix.scrollview import ScrollView

COLOR_DICT = {  "0" : "red", "1" : "yellow",
                "2" : "green", "3" : "purple",
                "4" : "blue", "5" : "cyan",
                "6" : "pink", "7" : "orange"}    
PICTURES_LIST = ["./Pictures/emptyWhite.png",
                 "./Pictures/rectangle.png"]

SCORES_LIST = "scores.json"

class ColorButton(Button):
    '''Just a normal button with the option to choose a color name as string'''
    def __init__(self):
        super().__init__()
        self.colorname = ""

class MastermindScreen(Screen):
    def __init__(self, **kwargs):
        super(MastermindScreen, self).__init__(**kwargs)
        self.admin_activated = False
        self.admin_combination = []
        self.player_name = ""
        self.button_index = 0  # Index counter - goes through every selectionbutton and starts at 0 once it reached the end
        self.game_state = 0  # Counter that stops the game if all the Playfield buttons are filled 
        self.winstreak = 0  # Extra winstreak counter for the player to see how many times they won in a row
        self.selection_buttons = [ColorButton() for i in range(8)]  # Buttons for the player to choose a color from
        self.tried_combinations = [ColorButton() for i in range(28)]  # Playfield that shows the combinations the player tried
        self.selected_buttons = [ColorButton() for i in range(4)]  # Field that shows the colors the player has chosen but not submitted in yet
        self.help_grid = [ColorButton() for i in range (28)]  # Helpfield that tells the player if they got an exact or contained hit
        self.submit_button = Button(text="Submit",bold=True, size_hint=(0.3,0.1),pos_hint={'x': .685, 'y': .22}, on_release=self.submit_colors,background_normal=PICTURES_LIST[1], background_color="blue")
        self.delete_button = Button(text="Delete Selection",bold=True, size_hint=(0.2,0.09),pos_hint={'x': .33, 'y': .06}, on_release=self.delete_input,background_normal=PICTURES_LIST[1], background_color="red")
        self.restart_button = Button(text="Restart",bold=True, size_hint=(0.3,0.1),pos_hint={'x': .685, 'y': .88}, on_release=self.restart_game,background_normal=PICTURES_LIST[1], background_color="purple")
        self.admin_button = Button(text="",size_hint=(0.1,0.05),pos_hint={'x': .01, 'y': .25}, on_release=self.admin_stuff,background_color="black")
        self.end_label = Label(text = "Red: exact hit\nYellow: contains color",size_hint=(0.3,0.1),pos_hint={'x': .68, 'y': .62},font_size = '26sp')
        self.winstreak_label = Label(text = f"Winstreak: {self.winstreak}",size_hint=(0.3,0.1),pos_hint={'x': .75, 'y': .3},font_size = '22sp', bold=True)
        self.name_textinput = TextInput(text='Name here (Confirm with Enter)', multiline=False, size_hint=(0.3,0.05), pos_hint={'x': .685, 'y': .4}, on_text_validate=self.submit_name)
        self.scoreboard_button = Button(text="Show Scoreboard", bold=True, size_hint=(0.3, 0.1), pos_hint={'x': .685, 'y': .45}, on_release=self.show_scoreboard)

        # Using the functions to initialize the different grids
        # Also adding everything into the window
        self.add_widget(self.init_choose_grid())
        self.add_widget(self.init_playfield_grid())
        self.add_widget(self.init_selection_grid())
        self.add_widget(self.init_help_grid())
        self.add_widget(self.submit_button)
        self.add_widget(self.delete_button)
        self.add_widget(self.restart_button)
        self.add_widget(self.end_label)
        self.add_widget(self.winstreak_label)
        self.add_widget(self.admin_button)
        self.add_widget(self.name_textinput)
        self.add_widget(self.scoreboard_button)

        # Randomizing the four colors
        self.random_colors = self.generate_random_colors()
    
    def submit_name(self, *args):
        self.player_name = self.name_textinput.text
        self.name_textinput.text = "Current Player: " + self.player_name
        print(self.player_name)
    
    def restart_game(self, *args):
        '''Restarts the game by enabling all the buttons and changing their values back to the start'''
        self.button_index = 0
        self.game_state = 0
        self.random_colors = self.generate_random_colors()
        self.submit_button.disabled = False
        self.delete_button.disabled = False
        for i in range(28):
            self.tried_combinations[i].background_color = "white"
            self.help_grid[i].background_color = "black"
        for i in range(4):
            self.selected_buttons[i].background_color = "white"
            self.selection_buttons[i].disabled = False
            self.selection_buttons[i+4].disabled = False
        self.end_game()
             
    def init_choose_grid(self):
        '''Initializes the choosing buttons in a gridlayout and positions it'''
        choose_grid = GridLayout(cols=4, rows=2)
        choose_grid.size_hint = (0.3, 0.2)
        choose_grid.pos_hint = {"center_x": 0.84, "center_y": 0.11}
        for i, button in enumerate(self.selection_buttons):
            button.background_color = COLOR_DICT[str(i)]
            button.colorname = COLOR_DICT[str(i)]
            button.bind(on_release=self.choose_color)
            button.background_normal = PICTURES_LIST[0]
            choose_grid.add_widget(button)
        return choose_grid
    
    def init_playfield_grid(self):
        '''Initializes the playfield buttons in a gridlayout and positions it'''
        playfield_grid = GridLayout(cols=4, rows=7)
        playfield_grid.size_hint = (0.3, 0.6)
        playfield_grid.pos_hint = {"center_x": 0.17, "center_y": 0.61}
        for i, button in enumerate(self.tried_combinations):
            button.disabled = True
            button.background_disabled_normal = PICTURES_LIST[0]
            playfield_grid.add_widget(button)
        return playfield_grid
    
    def init_selection_grid(self):
        '''Initializes the selection buttons in a gridlayout and positions it'''
        selection_grid = GridLayout(cols=4, rows=1)
        selection_grid.size_hint = (0.3, 0.1)
        selection_grid.pos_hint = {"center_x": 0.17, "center_y": 0.11}
        for i, button in enumerate(self.selected_buttons):
            button.disabled = True
            button.background_disabled_normal = PICTURES_LIST[0]
            selection_grid.add_widget(button)
        return selection_grid
    
    def init_help_grid(self):
        '''Initializes the help buttons in a gridlayout and positions it'''
        help_grid = GridLayout(cols=4, rows=7)
        help_grid.size_hint = (0.1, 0.6)
        help_grid.pos_hint = {"center_x": 0.4, "center_y": 0.61}
        for i, button in enumerate(self.help_grid):
            button.disabled = True
            button.background_disabled_normal = PICTURES_LIST[0]
            button.background_color = "black"
            help_grid.add_widget(button)
        return help_grid
    
    def delete_input(self, button):
        '''Lets the user delete their selected colors'''
        self.button_index = 0
        for button in self.selected_buttons:
            button.background_color = "white"
            button.colorname = "white"
        if self.admin_combination == ["red","red","red","orange","orange","orange"]:
            self.admin_activated = True
        if self.admin_combination == ["orange","orange","orange","red","red","red"]:
            self.admin_activated = False
        self.admin_combination = []
        
    def choose_color(self, button):
        '''Lets the user choose a color for the selection'''
        if self.button_index == 4:
            self.button_index = 0
        self.selected_buttons[self.button_index].background_color = button.colorname
        self.selected_buttons[self.button_index].colorname = button.colorname
        self.button_index += 1
        self.admin_combination.append(button.colorname)
        
    def submit_colors(self, button):
        '''Submits the chosen colors'''
        checking_colors = []
        for x in range(4):
            self.tried_combinations[x+self.game_state].background_color = self.selected_buttons[x].background_color
            checking_colors.append(self.selected_buttons[x].colorname)
            self.selected_buttons[x].background_color = "white"
            self.selected_buttons[x].colorname = "white"
        self.check_game_state(checking_colors)
        self.button_index = 0
        
    def check_game_state(self, colors):
        '''Checks for any correctly chosen color'''
        counter = self.game_state
        exact_matches, contained_matches = mastermind_cmd.check_game_state(colors, self.random_colors)
        for i in range(exact_matches):
            self.help_grid[counter+i].background_color = "red"
        for i in range(contained_matches):
            self.help_grid[exact_matches+counter+i].background_color = "yellow"
        self.game_state += 4
        if exact_matches == 4:
            self.end_game(win=True)
        elif self.game_state == 28:
            self.end_game(win=False)
            
    def end_game(self, win=None):
        '''Disables all pressable buttons except reset and ends the game with win or lose'''
        if win is None:
            if self.end_label.text != "YOU WIN!!":
                self.winstreak = 0
            self.end_label.text = "Red: exact hit\nYellow: contains color"
        else:
            self.submit_button.disabled = True
            self.delete_button.disabled = True
            for button in self.selection_buttons:
                button.disabled = True
            for i, button in enumerate(self.selected_buttons):
                button.background_color = self.random_colors[i]
            if win:
                self.end_label.text = "YOU WIN!!"
                self.winstreak += 1
            elif win is False:
                self.end_label.text = "YOU LOSE!!"
                self.winstreak = 0
        self.winstreak_label.text = f"Winstreak: {self.winstreak}"
                
    def generate_random_colors(self):
        '''Choses 4 random colors from the selection buttons'''
        colors = []
        random_colors = []
        for x in self.selection_buttons:
            colors.append(x.colorname)
        while len(random_colors) < 4:
            random_colors.append(random.choice(colors))
        return random_colors
    
    def admin_stuff(self, *args):
        if not self.admin_activated:
            return
        for i, button in enumerate(self.selected_buttons):
            button.background_color = self.random_colors[i]
    
    def show_scoreboard(self, *args):
        self.manager.current = 'scoreboard'

class ScoreboardScreen(Screen):
    def __init__(self, **kwargs):
        super(ScoreboardScreen, self).__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.label = Label(text="Scoreboard",size_hint=(1, 0.3))
        self.btn_back = Button(text="Back to Main Screen", size_hint=(1, 0.1))
        self.btn_back.bind(on_press=self.back_to_main)
        layout.add_widget(self.label)
        layout.add_widget(self.btn_back)

        # Create a ScrollView to hold the layout
        scroll_view = ScrollView()

        # Create a GridLayout to organize the data in rows
        self.grid_layout = GridLayout(cols=2, size_hint_y=1.3)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        # Add headers to the layout
        self.grid_layout.add_widget(Label(text='Name', bold=True))
        self.grid_layout.add_widget(Label(text='Score', bold=True))

        # Read the JSON data from file and populate the layout
        with open(SCORES_LIST, 'r') as file:
            data = json.load(file)
            for player in data['players']:
                self.grid_layout.add_widget(Label(text=player['name']))
                self.grid_layout.add_widget(Label(text=str(player['score'])))

        # Add the grid layout to the ScrollView
        scroll_view.add_widget(self.grid_layout)

        # Add the ScrollView to the main layout
        layout.add_widget(scroll_view)

        self.add_widget(layout)

    def back_to_main(self, instance):
        self.manager.current = 'main'

class MastermindGUI(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MastermindScreen(name='main'))
        sm.add_widget(ScoreboardScreen(name='scoreboard'))
        return sm


if __name__ == "__main__":
    MastermindGUI().run()
