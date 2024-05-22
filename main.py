from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from src.colors import Colors
import gc
import os
import json
import websocket
import time
import random
import uuid

class Main:
    def start(self):
        # path_cache = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Google', 'Chrome', 'User Data')        
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--start-maximized")
        self.options.add_argument("disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--log-level=3")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--mute-audio")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()) ,options=self.options)
        self.driver.maximize_window()
        self.driver.get('https://www.segurobet.com/')
        sleep(10)
        os.system('cls')
        print(Colors.YELLOW+"--|| Iniciando o Chrome."+Colors.RESET)
    
    def carregar_contas(self):
        self.config = json.load(open('config.json'))
        print(Colors.YELLOW+"--|| Carregando dados de conta."+Colors.RESET)
        self.contas = []
        with open('contas.txt', 'r', encoding='utf-8') as arquivo:
            self.contas = [linha.strip().split(',') for linha in arquivo if linha.strip()]
        with open('frases.txt', 'r', encoding='utf-8') as frases:
            self.frases = [linha.strip() for linha in frases if linha.strip()]
        print(Colors.YELLOW+"--|| Contas carregadas"+Colors.RESET)
        print(Colors.YELLOW+"--|| Frases carregadas"+Colors.RESET)

    def montar_mensagem(self):
        while True:
            try:
                print(Colors.BLUE+"--|| Montando mensagem."+Colors.RESET)
                mensagem = self.config["nome_no_telegram"]+" 💸💸💸💸💸"
                mensagem+=self.frases[random.randint(0, len(self.frases))]
                mensagem+=self.frases[random.randint(0, len(self.frases))]        
                mensagem+=" "+ self.config["nome_no_telegram"]      
                return mensagem
            except: pass
    
    def logar(self, conta):
        print(Colors.YELLOW+"--|| Iniciando login na plataforma."+Colors.RESET)
        tela_principal = self.driver.window_handles[0]
        try:
            sleep(3)
            self.driver.switch_to.frame(self.driver.find_elements(By.CSS_SELECTOR, 'iframe')[-1])
            sleep(1)
            self.driver.find_elements(By.CSS_SELECTOR, '.sb-close')[0].click()
            sleep(1)
        except: pass  
        self.driver.switch_to.window(tela_principal)
        self.driver.find_elements(By.CSS_SELECTOR, 'button.v3-login-btn')[0].click()
        sleep(1)
        self.driver.find_elements(By.CSS_SELECTOR, 'input#username')[0].click()
        self.driver.find_elements(By.CSS_SELECTOR, 'input#username')[0].send_keys(conta[0].strip())
        sleep(1)
        self.driver.find_elements(By.CSS_SELECTOR, 'input#password')[0].click()        
        self.driver.find_elements(By.CSS_SELECTOR, 'input#password')[0].send_keys(conta[1].strip())
        sleep(2)
        self.driver.find_elements(By.CSS_SELECTOR, 'button[type="submit"]')[0].click()
        sleep(5)
        
    def entrar_no_jogo(self):
        print(Colors.YELLOW+"--|| Entrando na área de jogo."+Colors.RESET)
        self.driver.get('https://www.segurobet.com/cassino/slots/all/28/evolution/57245-420032042-bac-bo-ao-vivo?provider=EVL&mode=real')
        sleep(5)
        self.driver.get('https://bwl.evo-games.com/frontend/evo/r2/#provider=evolution&ua_launch_id=17d1d1347c76e73e2d585c64&game=bacbo&table_id=PorBacBo00000001&app=')
        sleep(5)
        self.entrar_iframe(self)
    
    def entrar_iframe(self):
        sleep(2)
        self.driver.switch_to.frame(self.driver.find_elements(By.CSS_SELECTOR, 'iframe')[0])
        sleep(1)
        # self.driver.switch_to.frame(self.driver.find_elements(By.CSS_SELECTOR, 'iframe')[0])
        # sleep(5)
        self.evo_video_sessionId = self.driver.execute_script("return localStorage.getItem('evo.video.sessionId');")
        while not self.evo_video_sessionId:
            self.evo_video_sessionId = self.driver.execute_script("return localStorage.getItem('evo.video.sessionId');")
            sleep(1)
        print(Colors.BLUE+"--|| Código de acesso:"+Colors.RESET+ Colors.GREEN + f" {self.evo_video_sessionId}"+ Colors.RESET)
    
    def gerar_identificador_unico():
        timestamp_ms = int(time.time() * 1000)
        random_value = random.randint(1000, 9999)
        identificador_unico = f"{timestamp_ms}-{random_value}"
        return identificador_unico

    def mandar_mensagem(self, mensagem, numero):
        try:
            jsonUp = {
                "id": self.gerar_identificador_unico(),
                "type": "chat.text",
            }
            jsonUp["args"] = {
                "mode": "common",
                "text": mensagem,
                "orientation": "landscape"    
            }
            jsonUp = json.dumps(jsonUp)
            
            self.ws.send(jsonUp)            

        except Exception as e:
            print(f"--|| Ocorreu um erro: {e}")
        finally:
            print(Colors.GREEN+f"--|| Mensagem {numero} enviada com sucesso."+Colors.RESET)            
            
    def main(self):
        self.carregar_contas(self)
        while True:
            try:
                for conta in self.contas:
                    self.start(self)            
                    self.logar(self, conta)
                    self.entrar_no_jogo(self)
                    print(Colors.BLUE+"--|| Conexão WebSocket estabelecida."+Colors.RESET)                                        
                    self.ws_url = f"wss://bwl.evo-games.com/public/chat/table/PorBacBo00000001/player/socket?EVOSESSIONID={self.evo_video_sessionId}&client_version=6.20240521.72304.41769-1b75fe2250"
                    self.ws = websocket.create_connection(self.ws_url)
                    for rajada in range(self.config["numero_de_rajadas"]):
                        print(Colors.BLUE+f"--|| RAJADA {rajada+1} INICIADA."+Colors.RESET)
                        for indiceMensagem in range(self.config['numero_de_mensagens']):
                            mensagem = self.montar_mensagem(self)
                            self.mandar_mensagem(self, mensagem, indiceMensagem+1)
                            sleep(self.config['intervalo_entre_mensagens'])
                            try:
                                if indiceMensagem % 15 == 0 and indiceMensagem != 0:
                                    self.driver.find_elements(By.CSS_SELECTOR, 'div[data-role="bacbo-bet-spot-Player"]')[0].click()
                                    print("--|  Clique contra inatividade concluído!")
                            except: 
                                try: self.driver.find_elements(By.CSS_SELECTOR, 'div[data-role="inactivity-message-wrapper"]')[0].click()
                                except: pass
                        print(Colors.BLUE+f"--|| Iniciando próxima rajada após o intervalo de {self.config['intervalo_entre_rajadas']} segundos."+Colors.RESET)
                        sleep(self.config['intervalo_entre_rajadas'])
                    self.driver.quit()
                    self.ws.close()
                    del self.driver
                    del self.ws
                    gc.collect()
                    print(Colors.BLUE+f"--|| Aguardando {self.config['intervalo_entre_contas']} segundos para proxima campanha")
                    sleep(self.config['intervalo_entre_contas'])
            except Exception as err: 
                print(err)
                self.ws.close()
                self.driver.quit()
                continue
                
if __name__ == '__main__':
    Main.main(Main)