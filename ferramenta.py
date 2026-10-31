import ssl
import socket
import  os
import time
import threading
from queue import Queue
from colorama import Fore, Back, Style, init
init(autoreset=True)
cadeado = threading.Lock()
fila = Queue()
yellow = Fore.YELLOW
green = Fore.GREEN
red = Fore.RED
blank = Fore.WHITE
black = Fore.BLACK
def filtro(quantidade):
    portas = range(1, quantidade + 1)
    for porta in portas:
        fila.put(porta)
def scann(IP, sem):
    while not fila.empty():
        try:
            porta = fila.get_nowait()
        except:
            break
        with sem:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.5)
                env = s.connect_ex((IP, porta))
                with cadeado:
                    if env == 0:
                        print(Fore.GREEN + Style.BRIGHT + "*" * 30)
                        print(f"Conexão bem sucedida\t porta {porta} está aberta")
                        print(Fore.GREEN + Style.BRIGHT + "*" * 30)
                    with open("relatorio.txt", "w") as r:
                        r.write("IP:{IP} | Porta: {porta}\n")        
            except Exception as e:
                pass
            finally:
                fila.task_done()
                s.close()
def scan_massivo():
    ip = input("Digite o IP/Dominio alvo: ")
    qtd = int(input("Digite ate qual porta deseja fazer o scan (1, 60000): "))
    filtro(qtd)
    inicio = time.time()
    if qtd <= 500:
        max = 20
    else:
        max = 65
    sem = threading.Semaphore(max)
    for i in range(max):
        t =  threading.Thread(target=scann, daemon=True, args=(ip, sem,))
        t.start()
    fila.join()
    tempo = time.time() - inicio
    print(Fore.YELLOW + f"Scan finalizado em {tempo:.2f}s")
"""-------------------------------------------------------"""
def http_req(metodo, ip, porta):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, porta))
        print(f"Conectado em {ip}|{porta}")
        pkt = (
            f"{metodo} / HTTP/1.1\r\n"
            "host: {ip}\r\n"
            "User-Agent: NickkTry/1.0\r\n"
            "connection: close\r\n"
            "\r\n"
              )
        s.send(pkt.encode("utf-8"))
        resposta = s.recv(4080).decode("utf-8", errors="ignore")
        print (f"Resposta do servidor: {resposta}")
    except Exception as e:
        print(f"Houve um erro", e)

def scan_http():
    ip = input("Digite o IP/Dominio: ")
    porta = int(input("Digite a porta: "))
    method = input("Digite o metodo(GET or HEAD): ").upper()
    if method not in ["GET", "HEAD"]:
        print("Digite HEAD ou GET")
    t = threading.Thread(target=http_req, daemon=True, args=(method, ip, porta,))
    t.start()
    t.join()

"""------------------------------------------------------"""
def banner_grabing():
    ip = input("Digite o IP/Dominio alvo: ")
    porta = int(input("Digite a porta alvo: "))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if porta == 443:
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=ip)
        s.connect((ip, porta))
        pacote = ("HEAD / HTTP/1.1\r\n"
                 f"Host: {ip}\r\n"
                 "User-Agent: Scanner_NickkTry/1.0\r\n"
                 " Connection: close\r\n\r\n")
        s.send(pacote.encode())
        banner = s.recv(1024).decode(errors="ignore").strip()
        if banner:
            print(Fore.RED + Style.BRIGHT + "*" * 30)
            print(f"Banner da porta {porta}:\n{banner}...")
            print(Fore.RED + Style.BRIGHT + "*" * 30)
        return banner
    except:
        return None
    finally:
        s.close()

"""-----------------------------------------------------"""
sub_fila = Queue()

subs = [    "www", "m", "mail", "api", "blog", "cdn", "app", "video",
    "admin", "login", "portal", "ftp", "srv", "server", "cloud",
    "docs", "dev", "staging", "test", "mobile", "news", "shop",    
    "store", "payment", "cdn1", "cdn2", "media", "static", "img",
    "ns1", "ns2", "dns", "mx", "smtp", "webmail", "secure"]

def scan(dominio):
     while not sub_fila.empty():
         sub = sub_fila.get()
         completo = f"{sub}.{dominio}"
         
         try:
             nome, apelido, ips = socket.gethostbyname_ex(completo)
             for ip in ips:
                 print(Fore.RED + Style.BRIGHT + f"[ + ] {completo:30} →" + Fore.WHITE + f"{ip}")
         except Exception:
             pass
         
         sub_fila.task_done()
def testar(dominio):
     for s in subs:
         sub_fila.put(s)
     
     inicio = time.time()
     
     
     for _ in range(5):
         t = threading.Thread(target=scan, args=(dominio,), daemon=True)
         t.start()
     
     sub_fila.join()  
     
     fim = time.time()
     print(Fore.GREEN + f"\n✅ Pronto! Tempo: {fim - inicio:.2f}s")

def verificar_servidores():
     print(Fore.BLACK + Back.WHITE + "=== Varredura de Subdomínios ===")
     dominio = input("Digite o domínio (ex: tiktok.com): ")
     testar(dominio)
"""--------------------------------------------------------------"""

def testar_versao_navegador(porta=80):
    """Testa como o servidor responde a navegadores/dispositivos antigos"""
    ip_alvo = input("Digite o IP ou Dominio: ")    
    agentes = [
        ("Navegador Moderno", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
        ("Navegador Antigo", "Mozilla/4.0 (compatible; MSIE 6.0; Windows XP)"),
        ("Celular Antigo", "Mozilla/5.0 (SymbianOS/9.1; Series60/3.0 NokiaN73-1/3.0652.0.0)"),
        ("Dispositivo Muito Antigo", "BlackBerry8520/4.6.1.272 Profile/MIDP-2.0 Configuration/CLDC-1.1"),
        ("Sem Identidade", "-"),
    ]

    print(f"\n🔍 Testando: {ip_alvo}:{porta}")
    print("-" * 55)

    for nome, agente in agentes:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            
            if porta == 443:
                import ssl
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=ip_alvo)

            s.connect((ip_alvo, porta))
            
            requisicao = (
                f"GET / HTTP/1.1\r\n"
                f"Host: {ip_alvo}\r\n"
                f"User-Agent: {agente}\r\n"
                "Connection: close\r\n"
                "\r\n"
            )
            
            s.send(requisicao.encode())
            resposta = s.recv(1024).decode("utf-8", errors="ignore")
            s.close()

            linha1 = resposta.split("\n")[0]
            codigo = linha1.split(" ")[1] if len(linha1.split(" ")) > 1 else "???"

            
            if codigo in ["200", "301", "302"]:
                status = green + "[ + ] ACEITO"
            elif codigo in ["403", "406", "405"]:
                status = red + "[ + ] BLOQUEADO"
            elif codigo in ["404"]:
                status = Fore.YELLOW + "[ + ]  Não encontrado"
            else:
                status = f"[ - ] {codigo}"
            print(Back.WHITE + Fore.BLACK + "#" * 60)
            print(red + f"{nome:<22} →" + blank + f" {status}")
            print(resposta)
            print(resposta + "\n")
            
        except Exception as e:
            print(f"{nome:<22} →  Sem resposta")
        
    print("-" * 55)
    print(Fore.BLACK + Back.WHITE + "Teste finalizado!\n")
"""------------------------------------------------------"""

def menu_principal():
    print( "\n\t    #####  #  #   #  #  #  ##### ")
    print( "\t      #   #     ##  #  #  #  #   # ")
    print( "\t      #####  #  # # #  ####  #####  ") 
    print( "\t      #      #  #  ##  #  #  #   #")
    print( "\t      #      #  #   #  #  #  #   #\n")
    while True: 
        print("(0) - Limpar Terminal")
        print("(1)" + green + " - Scan de portas")
        print("(2)" + green + " - Respostas http")
        print("(3)" + green + " - Banner Grabbing")
        print("(4)" + green + " - Scan de Subdominio")
        print("(5)" + green + " - Testar vulnerabilidades de compatibilidade")
        try:
            usuario = int(input("Escolha uma opção: "))
            if usuario == 0:
                os.system("clear")
                continue
            elif usuario == 1:
                scan_massivo()
            elif usuario == 2:
                scan_http()
            elif usuario == 3:
                banner_grabing()
            elif usuario == 4:
                verificar_servidores()
            elif usuario == 5:
                testar_versao_navegador()
             
        except ValueError:
            print("Digite apenas " + yellow + Style.BRIGHT + "números")
        except KeyboardInterrupt:
            print(yellow + "\nScript encerrado com ^C")
            break
menu_principal()

