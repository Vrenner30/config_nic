import serial
import time
import sys

# CONFIGURACAO DA PORTA SERIAL 
# IMPORTANTE: Altere a 'COM_PORT' para a porta que seu equipamento usa.
COM_PORT = 'COM3'  # exemplo: 'COM3' no Windows ou '/dev/ttyUSB0' no Linux
BAUD_RATE = 9600   # velocidade padrao (ajuste se seu equipamento usar 115200)

def conectar_serial():
    """Tenta abrir a conexao serial."""
    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
        print(f"--- Conectado com sucesso na {COM_PORT} ---")
        return ser
    except serial.SerialException as e:
        print(f"Erro ao abrir a porta {COM_PORT}: {e}")
        print("Verifique se o Tera Term esta fechado (ele pode estar ocupando a porta).")
        sys.exit()

def send_cmd(ser, cmd, wait_time=1):
    """Envia um comando e aguarda um tempo."""
    print(f"Enviando: {cmd}")
    full_cmd = cmd + '\r\n' # Adiciona Enter (CR+LF)
    ser.write(full_cmd.encode('utf-8'))
    time.sleep(wait_time)

def send_raw(ser, text, wait_time=1):
    """Envia texto sem quebra de linha automatica (para o '@@@')."""
    print(f"Enviando Raw: {text}")
    ser.write(text.encode('utf-8'))
    time.sleep(wait_time)

# 2. ROTINA DE ACORDAR 
def wake_up_device(ser):
    print("\n--- Acordando Equipamento ---")
    send_raw(ser, '@@@', 1)
    send_cmd(ser, '', 1) # Sendln vazio
    print("Equipamento acordado.")

# 3. CONFIGURACOES ESPECIFICAS 
def config_mato_grosso(ser):
    print("\n--- Iniciando Configuracao MATO GROSSO ---")
    commands = [
        '$userdef,----,ENERGISA MT,00000000',
        '$simlib,1,ENERGISA.CLARO.COM.BR,10.200.1.204,40001,0,rs2000,rs2000,895505',
        '$simlib,2,TIM.BR,191.6.4.114,40001,0,rs2000,rs2000,895502',
        '$simlib,3,smart.m2m.vivo.com.br,191.6.4.114,40001,1,vivo,vivo,895506',
        '$simlib,4,gprs.oi.com.br,191.6.4.114,40001,0,rs2000,rs2000,895531',
        '$simlib,5,zap.vivo.com.br,191.6.4.114,40001,1,vivo,vivo,895511',
        '$simlib,6,zap.vivo.com.br,191.6.4.114,40001,1,vivo,vivo,895523',
        '$protocols,1,11,99,0,1',
        '$CHANNELS,1,6',
        '$scheds,1,6,31,0,86400',
        '$scheds,1,3,10,0,900',
        '$scheds,1,4,93,0,600',
        '$scheds,1,7,30,01112025000000,1'
    ]
    
    for cmd in commands:
        send_cmd(ser, cmd)

def config_sao_paulo(ser):
    print("\n--- Iniciando Configuracao SAO PAULO ---")
    commands = [
        '$userdef,----,CLIENTE SP,00000000',
        '$simlib,1,APN.SP.COM.BR,10.0.0.1,40001,0,user,pass,12345'
    ]
    for cmd in commands:
        send_cmd(ser, cmd)

def config_rio_janeiro(ser):
    print("\n--- Iniciando Configuracao RIO DE JANEIRO ---")
    commands = [
        '$userdef,----,CLIENTE RJ,00000000',
        '$simlib,1,APN.RJ.COM.BR,10.0.0.2,40001,0,user,pass,67890'
    ]
    for cmd in commands:
        send_cmd(ser, cmd)

# 4. SALVAR E REINICIAR 
def save_and_restart(ser):
    print("\n--- Salvando e Reiniciando ---")
    send_cmd(ser, '$save', 5)
    send_cmd(ser, '$restart')
    
    print("O equipamento esta reiniciando. Aguarde a verificacao automatica (40s)...")
    time.sleep(41)
    
    # Re-acorda
    wake_up_device(ser)
    
    # Verificacao
    print("--- Verificando Status ---")
    send_cmd(ser, '$vers', 1)
    send_cmd(ser, '$gsimlib', 1)
    
    # Leitura da resposta (Opcional: mostrar o que o equipamento respondeu)
    if ser.in_waiting > 0:
        resposta = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        print(f"\nRESPOSTA DO EQUIPAMENTO:\n{resposta}")
    
    print("\nProcesso Finalizado! Verifique as respostas acima.")

# --- FLUXO PRINCIPAL (MAIN) ---
def main():
    print("   AUTOMACAO NIC - PYTHON     ")

    print("1. Mato Grosso (Energisa)")
    print("2. Sao Paulo (Exemplo)")
    print("3. Rio de Janeiro (Exemplo)")
    print("4. Sair")
    
    opcao = input("\nSelecione o estado para configurar (1-4): ")

    if opcao == '4':
        print("Saindo...")
        return

    # Abre a conexão serial (Substitui abrir o Tera Term)
    ser = conectar_serial()

    try:
        # 1. Acorda
        wake_up_device(ser)

        # 2. Seleciona Configuração
        if opcao == '1':
            config_mato_grosso(ser)
        elif opcao == '2':
            config_sao_paulo(ser)
        elif opcao == '3':
            config_rio_janeiro(ser)
        else:
            print("Opcao invalida.")
            ser.close()
            return

        # 3. Salva e Reinicia
        save_and_restart(ser)

    except Exception as e:
        print(f"Ocorreu um erro durante a execucao: {e}")
    finally:
        ser.close()
        print("\nConexao serial fechada.")

if __name__ == "__main__":
    main()