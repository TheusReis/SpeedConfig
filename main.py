from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label  # Importe Label aqui
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from playwright.sync_api import sync_playwright
import time

class ConfigModemApp(App):
    def configure_modem(self, wifi_name, wifi_password, pppoe_config, modem_password):
        self.wifi_name = wifi_name
        self.wifi_password = wifi_password
        self.pppoe_config = pppoe_config
        self.modem_password = modem_password

        # Inicie a configuração do modem
        self.popup = Popup(title='Configurando Modem', content=Label(text='Aguarde...'), auto_dismiss=False)
        self.popup.open()
        Clock.schedule_once(self.run_playwright, 1)  # Inicia o processo após 1 segundo

    def run_playwright(self, dt):
        # Lista de substituições desejadas
        new_config = [("name_wi-fi_python", f'{self.wifi_name} 2.4G'), ("wi-fi_name_python_5G", f'{self.wifi_name} 5G'), ("pass_wi-fi_python", self.wifi_password), ("wan_config", self.pppoe_config)]

        # Abrir o arquivo em modo de leitura
        with open("config_huawei.txt", "r") as arquivo:
            # Ler o conteúdo do arquivo
            conteudo = arquivo.read()

        # Realizar as substituições
        for config in new_config:
            initial_config, end_config = config
            conteudo = conteudo.replace(initial_config, end_config)

        # Abrir o arquivo em modo de escrita
        with open("config_huawei.xml", "w") as arquivo:
            # Escrever o conteúdo modificado de volta para o arquivo
            arquivo.write(conteudo)

        # Configurando modem
        def handle_popup(dialog):
            dialog.accept()

        with sync_playwright() as playwright:
            # Define Chrome browser options
            options = {
                'args': [
                    '--ignore-certificate-errors',
                    '--disable-extensions',
                ],
                'headless': True  # Set headless option here
            }

            # Launch Chrome browser with options
            browser = playwright.chromium.launch(**options)
            page = browser.new_page()
            page.on('dialog', lambda dialog: handle_popup(dialog))
            page.goto('http://192.168.18.1')
            page.fill('//*[@id="txt_Username"]', "Epadmin")
            page.fill('//*[@id="txt_Password"]', str(self.modem_password.text))
            page.keyboard.press('Enter')
            time.sleep(3)

            # Upload File
            page.goto('https://192.168.18.1:80/html/ssmp/cfgfile/cfgfile.asp')
            time.sleep(3)
            input_element = page.locator('input[type="file"]')
            input_element.set_input_files('config_huawei.xml')
            time.sleep(1)
            page.locator('xpath=//*[@id="btnSubmit"]').click()

        self.popup.dismiss()  # Fecha a janela pop-up após a configuração

    def build(self):
        return Builder.load_file('main.kv')

if __name__ == '__main__':
    ConfigModemApp().run()
