import subprocess
import time


  def run_birdc_command(command):
    result = subprocess.run(['birdc', *command.split()], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Ощибка выполнения команды 'birdc {command}': {result.stderr}")
    return result.stdout

  def get_bgp_protocols():
    output = run_birdc_command("show proto")
    bgp_protocols = []
    for line in output.splitlines()[1:]:
        fields = line.split()
        if len(fields) >= 6 and fields[1] == "BGP":
            bgp_protocols.append(fields[0])
    return bgp_protocols

  def get_protocol_state(proto_name):
    status_output = run_birdc_command("show proto")
    for line in status_output.splitlines()[1:]:
        fields = line.split()
        if len(fields) >= 6 and fields[0] == proto_name:
            return fields[5]
    return None

  def reload_and_wait(proto_name):
    run_birdc_command(f"reload out {proto_name}")
    
    max_attempts = 6
    attempt = 0
    
    while attempt < max_attempts:
        state = get_protocol_state(proto_name)
        if state == "Established":
            print(f"Протокол {proto_name}: состояние {state}")
            return True
        else:
            attempt += 1
            print(f"Протокол {proto_name}: текущее состояние {state}, попытка {attempt}/{max_attempts}, таймаут 10 сек...")
            time.sleep(10)
    
    print(f"Ошибка: Протокол {proto_name} не перешел в состояние Established за {max_attempts} попыток.")
    return False

  def main():
    run_birdc_command("configure soft")
    bgp_protocols = get_bgp_protocols()
    if not bgp_protocols:
        print("Нет активных протоколов BGP.")
        return
    
    for proto in bgp_protocols:
        if not reload_and_wait(proto):
            print(f"Прерываю выполнение из-за ошибки с протоколом {proto}.")
            return

  if __name__ == "__main__":
    main()