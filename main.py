import paramiko
import configparser
import os
import stat
import gzip

def download_all_recursive(hostname, port, username, password, remote_directory, local_directory):
    try:
        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username, password=password)

        sftp = paramiko.SFTPClient.from_transport(transport)

        os.makedirs(local_directory, exist_ok=True)

        download_recursive(sftp, remote_directory, local_directory)

        print("Download complete!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if 'sftp' in locals():
            sftp.close()
        if 'transport' in locals():
            transport.close()

def download_recursive(sftp, remote_directory, local_directory):
    # List files and subdirectories in the remote directory
    files_and_dirs = sftp.listdir_attr(remote_directory)

    for item in files_and_dirs:
        item_name = item.filename
        remote_item_path = f"{remote_directory}/{item_name}"
        local_item_path = os.path.join(local_directory, item_name)

        if stat.S_ISDIR(item.st_mode):
            continue
            # os.makedirs(local_item_path, exist_ok=True)
            #
            # download_recursive(sftp, remote_item_path, local_item_path)
        else:
            if not os.path.exists(local_item_path):

                sftp.get(remote_item_path, local_item_path)
                if local_item_path.lower().endswith('.gz'):
                    # Extract the contents of the .gz file
                    with gzip.open(local_item_path, 'rb') as f_in:
                        with open(local_item_path[:-3], 'wb') as f_out:  # Remove .gz extension
                            f_out.write(f_in.read())
                    os.remove(local_item_path)
                #logging.info(f"Downloaded: {local_item_path}")

            else:
                #logging.info(f"Skipped: {local_item_path} (File already exists)")
                continue

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")

    sftp_host = config.get("SFTP", "hostname")
    sftp_port = int(config.get("SFTP", "port"))
    sftp_user = config.get("SFTP", "username")
    sftp_pass = config.get("SFTP", "password")
    remote_directory = config.get("SFTP", "remote_directory")
    local_directory = config.get("SFTP", "local_directory")

    download_all_recursive(sftp_host, sftp_port, sftp_user, sftp_pass, remote_directory, local_directory)
