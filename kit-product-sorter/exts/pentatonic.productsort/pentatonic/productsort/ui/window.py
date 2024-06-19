import omni.ui as ui
import omni.usd
import carb
import carb.events
import omni.kit.app
import omni
import os
import asyncio
from omni.kit.window.popup_dialog.form_dialog import FormDialog
from pxr import Gf
 
#Import extension scripts
from ..controllers.character_controls import CharacterController
from ..controllers.floating_camera import FloatingCamera
from ..scanners_sensors.barcode_scanner import BarcodeScanners
from ..scanners_sensors.proximity_sensors import ProximitySensors
from ..utilities.product_spawner import ProductSpawner

from .style import gen_ai_style, guide

from ..utilities.product_creation import spawn_container, spawn_products_in_container, spawn_products_in_hopper

class GenAIWindow(ui.Window):
    def __init__(self, title: str, **kwargs) -> None:
        super().__init__(title=title, **kwargs)

        event_type = carb.events.type_from_string("omni.kit.livestream.receive_message")
        message_bus = omni.kit.app.get_app().get_message_bus_event_stream()
        sub = message_bus.create_subscription_to_pop_by_type(event_type, self.on_event)

        settings = carb.settings.get_settings()
        os.environ["OPENAI_API_KEY"] = settings.get_as_string("/persistent/exts/pentatonic.productsort/OpenAI_APIKey")
        os.environ["AWS_VAMS_PATH"] = settings.get_as_string("/persistent/exts/pentatonic.productsort/aws_vams_path")
        os.environ["AWS_S3_PATH"] = settings.get_as_string("/persistent/exts/pentatonic.productsort/aws_s3_path")

        self._target_pos_text = "(0.00, 0.00, 0.00)"
        self._target_pos = Gf.Vec3d(0, 0, 0)
        self._target_rot = Gf.Vec3d(0, 0, 0)
        self._target_rigidBody = ""
        self._hopper_title = "Start"
        self._hopper_state = False
        
        self._controller = None
        self._floating_camera = FloatingCamera(self)
        self._floating_camera.toggle_floating_camera(True)

        self._barcode_scanners = BarcodeScanners(self)
        self._proximity_sensors = ProximitySensors(self)
        self._product_spawner = ProductSpawner(self)

        self.cct_path = "/World/ThridPerson"

        # Models
        self._prompt_model = ui.SimpleStringModel("")
        self._product_name_model = ui.SimpleStringModel()
        self._use_local_nucleus = ui.SimpleBoolModel(default_value = True)

        # Initial Value = False
        self._third_person = ui.SimpleBoolModel(default_value = False)
        self._live_preview = ui.SimpleBoolModel(default_value = False)
        self._previous_third_person_state = self._third_person.as_bool

        self._update_stream = omni.kit.app.get_app().get_update_event_stream()
        self._update_subscription = self._update_stream.create_subscription_to_pop(self.on_update)

        self._using_isaac = ui.SimpleBoolModel(default_value = True)

        # Lego Models
        self._lego_random = ui.SimpleBoolModel(default_value = True)
        self._1x1_plate = ui.SimpleBoolModel(default_value = False)
        self._1x2_block = ui.SimpleBoolModel(default_value = False)
        self._2x3_block = ui.SimpleBoolModel(default_value = False)
        self._2x2_45block = ui.SimpleBoolModel(default_value = False)
        self._2x4_plate = ui.SimpleBoolModel(default_value = False)
        self._6x8_plate = ui.SimpleBoolModel(default_value = False)

        # Loreal Models
        self._loreal_random = ui.SimpleBoolModel(default_value = True)
        self._shampoo_bottle_1 = ui.SimpleBoolModel(default_value = False)
        self._shampoo_bottle_2 = ui.SimpleBoolModel(default_value = False)
        self._lotion_bottle_small = ui.SimpleBoolModel(default_value = False)
        self._lotion_bottle_large = ui.SimpleBoolModel(default_value = False)
        self._lotion_jar = ui.SimpleBoolModel(default_value = False)

        # Liquid Material Models
        self._motor_oil = ui.SimpleBoolModel(default_value = False)
        self._vegetable_oil = ui.SimpleBoolModel(default_value = False)
        self._paint_thinner = ui.SimpleBoolModel(default_value = False)
        self._ethanol = ui.SimpleBoolModel(default_value = False)
        self._acetone = ui.SimpleBoolModel(default_value = False)
        self._methanol = ui.SimpleBoolModel(default_value = False)
        self._glycerol = ui.SimpleBoolModel(default_value = False)
        self._ethylene_glycol = ui.SimpleBoolModel(default_value = False)
        self._diesel = ui.SimpleBoolModel(default_value = False)
        self._gasoline = ui.SimpleBoolModel(default_value = False)
        self._kerosene = ui.SimpleBoolModel(default_value = False)
        self._lubricating_oil = ui.SimpleBoolModel(default_value = False)
        self._antifreeze = ui.SimpleBoolModel(default_value = False)
        self._toluene = ui.SimpleBoolModel(default_value = False)
        self._xylene = ui.SimpleBoolModel(default_value = False)
        self._hydraulic_fluids = ui.SimpleBoolModel(default_value = False)
        self._cleaning_agents = ui.SimpleBoolModel(default_value = False)
        self._water_based_adhesives = ui.SimpleBoolModel(default_value = False)
        self._alcohol_based_inks = ui.SimpleBoolModel(default_value = False)
        self._bleach = ui.SimpleBoolModel(default_value = False)

        # Plastic Material Models
        self._polyethylene = ui.SimpleBoolModel(default_value = False)
        self._polypropylene = ui.SimpleBoolModel(default_value = False)
        self._polyethylene_terephthalate = ui.SimpleBoolModel(default_value = False)
        self._polyvinyl_chloride = ui.SimpleBoolModel(default_value = False)
        self._polystyrene = ui.SimpleBoolModel(default_value = False)
        self._nylon = ui.SimpleBoolModel(default_value = False)
        self._acrylic = ui.SimpleBoolModel(default_value = False)
        self._polycarbonate = ui.SimpleBoolModel(default_value = False)
        self._polyurethane = ui.SimpleBoolModel(default_value = False)
        self._high_impact_polystyrene = ui.SimpleBoolModel(default_value = False)
        self._abs = ui.SimpleBoolModel(default_value = False)
        self._polyamide = ui.SimpleBoolModel(default_value = False)
        self._polylactic_acid = ui.SimpleBoolModel(default_value = False)
        self._polyether_ether_ketone = ui.SimpleBoolModel(default_value = False)
        self._polyvinylidene_fluoride = ui.SimpleBoolModel(default_value = False)
        self._polyoxymethylene = ui.SimpleBoolModel(default_value = False)
        self._polytetrafluoroethylene = ui.SimpleBoolModel(default_value = False)
        self._polyetherimide = ui.SimpleBoolModel(default_value = False)
        self._polyphenylene_sulfide = ui.SimpleBoolModel(default_value = False)
        self._polyaryletherketone = ui.SimpleBoolModel(default_value = False)

        self._plastic_items = [
            ("Polyethylene", self._polyethylene),
            ("Polypropylene", self._polypropylene),
            ("Polyethylene Terephthalate", self._polyethylene_terephthalate),
            ("Polyvinyl Chloride", self._polyvinyl_chloride),
            ("Polystyrene", self._polystyrene),
            ("Nylon", self._nylon),
            ("Acrylic", self._acrylic),
            ("Polycarbonate", self._polycarbonate),
            ("Polyurethane", self._polyurethane),
            ("High Impact Polystyrene", self._high_impact_polystyrene),
            ("ABS", self._abs),
            ("Polyamide", self._polyamide),
            ("Polylactic Acid", self._polylactic_acid),
            ("Polyether Ether Ketone", self._polyether_ether_ketone),
            ("Polyvinylidene Fluoride", self._polyvinylidene_fluoride),
            ("Polyoxymethylene", self._polyoxymethylene),
            ("Polytetrafluoroethylene", self._polytetrafluoroethylene),
            ("Polyetherimide", self._polyetherimide),
            ("Polyphenylene Sulfide", self._polyphenylene_sulfide),
            ("Polyaryletherketone", self._polyaryletherketone)
        ]

        self._liquid_items = [
            ("Motor Oil", self._motor_oil),
            ("Vegetable Oil", self._vegetable_oil),
            ("Paint Thinner", self._paint_thinner),
            ("Ethanol", self._ethanol),
            ("Acetone", self._acetone),
            ("Methanol", self._methanol),
            ("Glycerol", self._glycerol),
            ("Ethylene Glycol", self._ethylene_glycol),
            ("Diesel", self._diesel),
            ("Gasoline", self._gasoline),
            ("Kerosene", self._kerosene),
            ("Lubricating Oil", self._lubricating_oil),
            ("Antifreeze", self._antifreeze),
            ("Toluene", self._toluene),
            ("Xylene", self._xylene),
            ("Hydraulic Fluids", self._hydraulic_fluids),
            ("Cleaning Agents", self._cleaning_agents),
            ("Water-based Adhesives", self._water_based_adhesives),
            ("Alcohol-based Inks", self._alcohol_based_inks),
            ("Bleach", self._bleach)
        ]

        self._lego_items = [
            ("All", self._lego_random),
            ("1x1 Plate", self._1x1_plate),
            ("1x2 Block", self._1x2_block),
            ("2x3 Block", self._2x3_block),
            ("2x2 45 Block", self._2x2_45block),
            ("2x4 Plate", self._2x4_plate),
            ("6x8 Plate", self._6x8_plate)
        ]

        self._loreal_items = [
            ("All", self._loreal_random),
            ("Large Bottle 1", self._shampoo_bottle_1),
            ("Large Bottle 2", self._shampoo_bottle_2),
            ("Lotion Bottle Short", self._lotion_bottle_small),
            ("Lotion Bottle Tall", self._lotion_bottle_large),
            ("Jar", self._lotion_jar)
        ]

        self.generation_template = {'product':'Lego', 'material_type': 'Plastics', 'materials':['ABS'], 'container':'Cardboard_Box', 'fill_percent': '50%', 'prompt': ''}

        #Used for the Materials drop down box and Scroll Wheel Actions (Thrid Person)
        self._materials = ['Random', 'Custom']
        self.current_material_index = 0
        self.current_material = 'Random'
        self._combo_material_changed_sub = None

        #Used for the Product Type drop down box and Scroll Wheel Actions (Thrid Person)
        self._products = ['Legos', "Loreal", 'Random']
        self.current_product_index = 0
        self.current_product = 'Legos'
        self._combo_product_changed_sub = None

        #Used for the Container Type drop down box and Scroll Wheel Actions (Thrid Person)
        self._containers = ['Cardboard_Box', 'Metal_Crate', 'Plastic_Bin', 'Random']
        self.current_container_index = 0
        self.current_container = 'Cardboard_Box'
        self._combo_container_changed_sub = None

        #Used for the Container Fill Percentage drop down box and Scroll Wheel Actions (Thrid Person)
        self._container_fills = ['50%', '10%', '20%', '30%', '40%', '60%', '70%', '80%', '90%', '100%', 'Random']
        self.current_container_fill_index = 0
        self.current_container_fill = '50%'
        self._combo_container_fill_changed_sub = None

        #Used for the Generations drop down box and Scroll Wheel Actions
        self._generations = ['None']
        self.current_generation_index = 0
        self.current_generation = 'None'
        self._combo_generation_changed_sub = None

        self._last_prompt = ""
        self._last_response = ""
        self.response_log = None

        self.product_list = []

        self._kb_event = ""
        self._kb_key1 = True
        self._kb_key2 = False
        self._on_right_mouse = False

        self._spawn_button = None
        
        self._generation_button_label = "Generate & Spawn"
        self._character_spawned = False
        self._floating_camera_spawned = False
        self._flag = True
        self.frames = 0
        self.floating_init = False

        self.frame.set_build_fn(self._build_fn)

    def on_update(self, e):
        self._is_playing = omni.timeline.get_timeline_interface().is_playing()

        if not self._third_person:
            return
        
        current_third_person_state = self._third_person.as_bool
        if current_third_person_state != self._previous_third_person_state:
            self._previous_third_person_state = current_third_person_state
            if current_third_person_state:
                self._floating_camera.toggle_floating_camera(False)
                if self._spawn_button is None:
                    with self.frame:
                        self._spawn_button = ui.Button("Spawn 3rd Person", height=40, clicked_fn=lambda: self._spawn_character(), style={"font_size": 18})
            else:
                if self._spawn_button is not None:
                    self._floating_camera.toggle_floating_camera(True)
                    self._live_preview.as_bool = False
                    self._spawn_button.visible = False
                    self._spawn_button = None
                    
            self.rebuild_frame()

        if not self._is_playing:
            return
        
    def on_event(self, event: carb.events.IEvent):
        print(event.payload)
        message = event.payload["setColor"]

        print("received", message)

    def set_key_command(self, event):
        if event == "CYCLE_UP":
            if self._kb_key1:
                self.current_product_index = (self.current_product_index + 1) % len(self._products)
            if self._kb_key2:
                self.current_material_index = (self.current_material_index + 1) % len(self._materials)
         
        if event == "CYCLE_DOWN":
            if self._kb_key1:
                self.current_product_index = (self.current_product_index - 1) % len(self._products)
            if self._kb_key2:
                self.current_material_index = (self.current_material_index - 1) % len(self._materials)

        if event == "KEY_1":
            self._kb_key1 = True
            self._kb_key2 = False
        
        if event == "KEY_2":
            self._kb_key1 = False
            self._kb_key2 = True

        self.rebuild_frame()

    def spawn_floating_camera(self):

        return
    
    def get_floating_cam_info(self):
        return
    
    def set_floating_cam_info(self):
        return
    
    # TODO: Change logic for distribution and spawning of container
    def set_target(self, position, rotation, rigidBody, onPlace):
        formatted_str = "({}, {}, {})".format(
            "{:.2f}".format(position[0]),
            "{:.2f}".format(position[1]),
            "{:.2f}".format(position[2])
        )

        self._target_pos = position
        self._target_rot = rotation
        self._target_pos_text = formatted_str
        self._target_rigidBody = rigidBody

        if onPlace:
            # Products
            if self.current_generation is not None and self.current_generation != 'None':
                
                prim, path = spawn_container(self.current_generation, self._target_pos, self._target_rot)
                spawn_products_in_container(self.current_generation, prim, path)

                self.rebuild_frame()
        else:
            self.rebuild_frame()
    
    def _create_product_list(self):
        self.product_list.clear()

        if self.current_product == "Legos":
            if self._lego_random.as_bool is True:
                self.product_list.append('Plate_1x1')
                self.product_list.append('Block_1x2')
                self.product_list.append('Block_2x3')
                self.product_list.append('Degree_2x2_45')
                self.product_list.append('Plate_2x4')
                self.product_list.append('Plate_6x8')

            else:
                if self._1x1_plate.as_bool is True:
                    self.product_list.append('Plate_1x1')
                if self._1x2_block.as_bool is True:
                    self.product_list.append('Block_1x2')
                if self._2x3_block.as_bool is True:
                    self.product_list.append('Block_2x3')
                if self._2x2_45block.as_bool is True:
                    self.product_list.append('Degree_2x2_45')
                if self._2x4_plate.as_bool is True:
                    self.product_list.append('Plate_2x4')
                if self._6x8_plate.as_bool is True:
                    self.product_list.append('Plate_6x8')

        elif self.current_product == "Loreal":
            if self._loreal_random.as_bool is True:
                self.product_list.append('Large_Bottle_1')
                self.product_list.append('Large_Bottle_2')
                self.product_list.append('Lotion_Bottle_Tall')
                self.product_list.append('Lotion_Bottle_Short')
                self.product_list.append('Jar')

            else:
                if self._shampoo_bottle_1.as_bool is True:
                    self.product_list.append('Large_Bottle_1')
                if self._shampoo_bottle_2.as_bool is True:
                    self.product_list.append('Large_Bottle_2')
                if self._lotion_bottle_small.as_bool is True:
                    self.product_list.append('Lotion_Bottle_Tall')
                if self._lotion_bottle_large.as_bool is True:
                    self.product_list.append('Lotion_Bottle_Short')
                if self._lotion_jar.as_bool is True:
                    self.product_list.append('Jar')

    def _build_fn(self):
        with self.frame:
            with ui.ScrollingFrame():
                with ui.VStack(style=gen_ai_style):
                    with ui.HStack(height=0):
                        ui.Label("Product Sort Simulation", style={"font_size": 18})
                        ui.Button(name="properties", tooltip="OpenAI, AWS settings, & output path for synthetic data", width=30, height=30, clicked_fn=lambda: self._open_settings())
                    
                    # Instructions
                    with ui.CollapsableFrame("Getting Started Instructions", height=0, collapsed=True):
                        ui.Label(guide, word_wrap=True)
                    
                    ui.Spacer(height=5)
                    with ui.HStack(height=0):
                        with ui.HStack(width=10):
                            ui.Label("Third Person:")
                            ui.CheckBox(model=self._third_person)

                        ui.Spacer(width=10)
                        with ui.HStack(width=10):
                            ui.Label("Isaac Sim:")
                            ui.CheckBox(model=self._using_isaac)

                        ui.Spacer(width=10)  
                        with ui.HStack(width=10):
                            ui.Label("Localhost:")
                            ui.CheckBox(model=self._use_local_nucleus)

                        
                        ui.Spacer(width=10)  
                        with ui.HStack(width=10):
                            if self._third_person.as_bool:
                                ui.Label("Live Preview:")
                                ui.CheckBox(model=self._live_preview)

                    if self._third_person.as_bool:
                        self._spawn_button = ui.Button("Spawn 3rd Person", height=40, clicked_fn=lambda: self._spawn_character(), style={"font_size": 18})
                    
                    ui.Button(self._hopper_title + " Hopper", height=40,clicked_fn=lambda: self._spawn_hopper(), style={"font_size": 18})

                    ui.Line(height=10)

                    with ui.HStack(height=0):
                        with ui.HStack(width=250):
                            ui.Label("Product Type:", tooltip="Select product from downdown")
                            self._build_product_combo_box()

                    if self.current_product == 'Legos' and self.current_product is not None:
                        self._build_lego_section()

                    if self.current_product == "Loreal" and self.current_product is not None:
                        self._build_loreal_section()
                     
                    
                    with ui.HStack(height=0):
                        with ui.HStack(width=250):
                            ui.Label("Material Type:", tooltip="Select material from downdown once checked")
                            self._build_material_combo_box()
                    
                    if self.current_material == 'Custom' and self.current_material is not None:
                        self._build_plastic_section()

                    ui.Line(height=10)

                    with ui.HStack(height=0):
                        with ui.HStack(width=250):
                            ui.Label("Container Type:", tooltip="Select product from downdown")
                            self._build_container_combo_box()
                    
                    with ui.HStack(height=0):
                        with ui.HStack(width=250):
                            ui.Label("Container Fill %:", tooltip="Select product from downdown")
                            self._build_container_fill_combo_box()
                    
                    ui.Line(height=10)

                    ui.Label("OpenAI Prompt", style={"font_size": 18})
                    with ui.HStack(height=ui.Percent(25)):
                        ui.StringField(model=self._prompt_model, multiline=True)

                    ui.Button("Create Generation", height=40,clicked_fn=lambda: self._apply_button(), style={"font_size": 18})  
                    
                    ui.Line()
                    
                    ui.Spacer(height=10)
                    ui.Label("Generations", style={"font_size": 18})        
                    with ui.HStack(height=0):
                        with ui.HStack(width=750):
                            self._build_generation_combo_box()

                    if self._third_person.as_bool is False:
                        ui.Button("Spawn Container W/Generation", height=40,clicked_fn=lambda: self._spawn_container_button(), style={"font_size": 18})  
                    ui.Line()

                    ui.Label("Selection Details", style={"font_size": 18})
                    with ui.HStack(height=0):
                        with ui.HStack(width=115):
                            ui.Label("Target Path: ")
                        ui.Label(self._target_rigidBody)

                    with ui.HStack(height=0):
                        with ui.HStack(width=115):
                            ui.Label("Target Position: ")
                        ui.Label(self._target_pos_text)

                    ui.Line()
                    
                    with ui.CollapsableFrame("ChatGPT Response / Log", height=0, collapsed=True, style={"font_size": 18}):
                        self.response_log = ui.Label("Prompt:\n" + self._last_prompt + "\n\nGenerated:\n" + self._last_response, word_wrap=True)
       
    def _build_lego_section(self):
        ui.Spacer(height=5)
        for i in range(0, len(self._lego_items), 2):
            with ui.HStack(height=0):
                for j in range(2):
                    if i + j < len(self._lego_items):
                        item_name, item_model = self._lego_items[i + j]
                        with ui.HStack(width=125):
                            ui.Label(item_name)
                        ui.CheckBox(model=item_model)
                        ui.Spacer()
                    ui.Spacer()
                
    def _build_loreal_section(self):
        ui.Spacer(height=5)
        for i in range(0, len(self._loreal_items), 2):
            with ui.HStack(height=0):
                for j in range(2):
                    if i + j < len(self._loreal_items):
                        item_name, item_model = self._loreal_items[i + j]
                        with ui.HStack(width=125):
                            ui.Label(item_name)
                        ui.CheckBox(model=item_model)
                        ui.Spacer()
                ui.Spacer()

    def _build_liquid_section(self):
        ui.Spacer(height=5)
        for i in range(0, len(self._liquid_items), 2):
            with ui.HStack(height=0):
                for j in range(2):
                    if i + j < len(self._liquid_items):
                        item_name, item_model = self._liquid_items[i + j]
                        with ui.HStack(width=200):
                            ui.Label(item_name)
                        ui.CheckBox(model=item_model)
                        ui.Spacer()
                    ui.Spacer()
        
    def _build_plastic_section(self):
        ui.Spacer(height=5)
        for i in range(0, len(self._plastic_items), 2):
            with ui.HStack(height=0):
                for j in range(2):
                    if i + j < len(self._plastic_items):
                        item_name, item_model = self._plastic_items[i + j]
                        with ui.HStack(width=200):
                            ui.Label(item_name)
                        ui.CheckBox(model=item_model)
                        ui.Spacer()
                    ui.Spacer()
    
    def rebuild_frame(self):
        # we do want to update the product name and possibly last prompt?
        self.frame.rebuild()
        self.response_log.text = self._last_response
        return
    

    def _spawn_hopper(self):
        print("Hopper Button")
        if self._hopper_state is False:
            print("Hopper Started")
            self._apply_button()
            self._hopper_title = "Stop"
            self._hopper_state = True
            self._product_spawner.on_toggle(True)

            
        elif self._hopper_state is True:
            print("Hopper Stopped")
            self._hopper_state = False
            self._hopper_title = "Start"
            self._product_spawner.on_toggle(False)
            
        self.rebuild_frame()

    def _spawn_character(self):
        stage = omni.usd.get_context().get_stage()

        print("Spawn Button")
        if self.current_generation is not None and self.current_generation == 'None':
            print("Spawn>Apply Button")
            self._apply_button()

        if self._character_spawned is False:
            print("Character Not Found")
            self._controller = CharacterController(self)

            self._controller.on_spawn(self._third_person.as_bool, self._using_isaac.as_bool, self._live_preview.as_bool, self.current_container)
            self._character_spawned = True

        self.rebuild_frame()

    def _spawn_container_button(self):
        # self._target_pos = Gf.Vec3d
        # Set Position
        default_pos = Gf.Vec3d((-2, 0, 0.8))
        if self._third_person.as_bool is False:
            prim, path = spawn_container(self.current_generation, default_pos, Gf.Vec3d(0,0,0))
        
    def _apply_button(self):
        self._create_product_list()
        # Cardboard Box, Filled at 50%, Legos:[1x1_Plate, 1x2_Block, 2x2_45_Degree], Materials: [ABS]

        data = {
            'container':self.current_container,
            'container_fill':self.current_container_fill,
            'product_type':self.current_product,
            'product_list':self.product_list
        }
        
        self._generations.append(data)
        self.current_generation_index += 1
        self.current_generation = self._generations[self.current_generation_index]

        self.rebuild_frame()

    def _build_product_combo_box(self):
        self.combo_product_model = ui.ComboBox(self.current_product_index, *[str(x) for x in self._products], width=ui.Percent(60)).model
        def combo_product_changed(item_model, item):
            index_value_model = item_model.get_item_value_model(item)
            self.current_product = str(self._products[index_value_model.as_int])
            self.current_product_index = index_value_model.as_int
            print(self.current_product)
            self.rebuild_frame()
        self._combo_product_changed_sub = self.combo_product_model.subscribe_item_changed_fn(combo_product_changed)

    def _build_material_combo_box(self):
        self.combo_material_model = ui.ComboBox(self.current_material_index, *[str(x) for x in self._materials], width=ui.Percent(60)).model
        def combo_material_changed(item_model, item):
            index_value_model = item_model.get_item_value_model(item)
            self.current_material = str(self._materials[index_value_model.as_int])
            self.current_material_index = index_value_model.as_int
            self.rebuild_frame()
        self._combo_material_changed_sub = self.combo_material_model.subscribe_item_changed_fn(combo_material_changed)

    def _build_container_combo_box(self):
        self.combo_container_model = ui.ComboBox(self.current_container_index, *[str(x) for x in self._containers], width=ui.Percent(60)).model
        def combo_container_changed(item_model, item):
            index_value_model = item_model.get_item_value_model(item)
            self.current_container = str(self._containers[index_value_model.as_int])
            self.current_container_index = index_value_model.as_int
            self.rebuild_frame()
        self._combo_container_changed_sub = self.combo_container_model.subscribe_item_changed_fn(combo_container_changed)

    def _build_container_fill_combo_box(self):
        self.combo_container_fill_model = ui.ComboBox(self.current_container_fill_index, *[str(x) for x in self._container_fills], width=ui.Percent(60)).model
        def combo_container_fill_changed(item_model, item):
            index_value_model = item_model.get_item_value_model(item)
            self.current_container_fill = str(self._container_fills[index_value_model.as_int])
            self.current_container_fill_index = index_value_model.as_int
            self.rebuild_frame()
        self._combo_container_fill_changed_sub = self.combo_container_fill_model.subscribe_item_changed_fn(combo_container_fill_changed)

    def _build_generation_combo_box(self):
        self.combo_generation_model = ui.ComboBox(self.current_generation_index, *[str(x) for x in self._generations], width=ui.Percent(60)).model
        def combo_generation_changed(item_model, item):
            index_value_model = item_model.get_item_value_model(item)
            self.current_generation = str(self._generations[index_value_model.as_int])
            self.current_generation_index = index_value_model.as_int
            self.rebuild_frame()
        self._combo_generation_changed_sub = self.combo_generation_model.subscribe_item_changed_fn(combo_generation_changed)

    def _save_settings(self, dialog):
        values = dialog.get_values()
        carb.log_info(values)

        settings = carb.settings.get_settings()

        settings.set_string("/persistent/exts/pentatonic.productsort/OpenAI_APIKey", values["OpenAI_APIKey"])
        os.environ["OPENAI_API_KEY"] = settings.get_as_string("/persistent/exts/pentatonic.productsort/OpenAI_APIKey")

        settings.set_string("/persistent/exts/pentatonic.productsort/aws_s3_path", values["aws_s3_path"])
        os.environ["AWS_S3_PATH"] = settings.get_as_string("/persistent/exts/pentatonic.productsort/aws_s3_path")

        settings.set_string("/persistent/exts/pentatonic.productsort/vams_path", values["aws_vams_path"])
        os.environ["AWS_VAMS_PATH"] = settings.get_as_string("/persistent/exts/pentatonic.productsort/aws_vams_path")

        settings.set_string("/persistent/exts/pentatonic.productsort/output_path", values["output_path"])
        dialog.hide()

    def _open_settings(self):
        settings = carb.settings.get_settings()   
        openai_apikey_value = settings.get_as_string("/persistent/exts/pentatonic.productsort/OpenAI_APIKey")
        aws_s3_path = settings.get_as_string("/persistent/exts/pentatonic.productsort/aws_s3_path")
        aws_vams_path = settings.get_as_string("/persistent/exts/pentatonic.productsort/aws_vams_path")
        output_path = settings.get_as_string("/persistent/exts/pentatonic.productsort/output_path")

        field_defs = [
            FormDialog.FieldDef("OpenAI_APIKey", "OpenAI API Key: ", ui.StringField, openai_apikey_value),
            FormDialog.FieldDef("aws_s3_path", "AWS S3 Path: ", ui.StringField, aws_s3_path),
            FormDialog.FieldDef("aws_vams_path", "AWS VAMs Path: ", ui.StringField, aws_vams_path),
            FormDialog.FieldDef("output_path", "Output Data Path: ", ui.StringField, output_path)
        ]        

        dialog = FormDialog(
            title="Settings",
            message="Your Settings: ",
            field_defs = field_defs,
            ok_handler=lambda dialog: self._save_settings(dialog))

        dialog.show()

    # Get the prompt specified
    def get_prompt(self):
        if self._prompt_model == "":
            carb.log_warn("No Prompt Provided")
        return self._prompt_model.as_string

    def reset(self):
        print("Reset Called")
        self.product_list = []
        self._prompt_model = None
        self._product_name_model = None
        self._use_local_nucleus = None
        self._materials = None
        self._products = None
        self.response_log = None
        self._combo_product_changed_sub = None
        self._combo_material_changed_sub = None

        stage = omni.usd.get_context().get_stage()
        if self._character_spawned is True and stage.GetPrimAtPath(self.cct_path):
            omni.kit.commands.execute('DeletePrimsCommand', paths=[self.cct_path])
        self._character_spawned = False

    def on_shutdown(self):
        if self._update_stream:
            self._update_stream.unsubscribe()

    def destroy(self):
        super().destroy()
        print("Destroy Called")
        self.product_list = []
        self._prompt_model = None
        self._product_name_model = None
        self._use_local_nucleus = None
        self._materials = None
        self._products = None
        self.response_log = None
        self._combo_product_changed_sub = None
        self._combo_material_changed_sub = None
        self._character_spawned = False

        stage = omni.usd.get_context().get_stage()
        if self._character_spawned is True and stage.GetPrimAtPath(self.cct_path):
            omni.kit.commands.execute('DeletePrimsCommand', paths=[self.cct_path])

        