from time import sleep
import subprocess

if __name__ == "__main__":
    #main()
    commands = [
        "rm -rf cloud",
        "git clone -b cloud --single-branch https://github.com/ktkhuong/sgparl.git cloud",
        "sudo chmod 777 cloud/data",
        #"cd cloud"
    ]
    batch = ";".join(commands)
    p = subprocess.Popen(f'plink -i ssh/sgparl_private.ppk -batch sgparl@35.230.145.133 "{batch}"', creationflags=subprocess.CREATE_NEW_CONSOLE)
    p.wait()

