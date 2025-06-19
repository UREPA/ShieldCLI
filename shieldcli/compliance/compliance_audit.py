import subprocess

def audit_checks():
    def run_cmd(cmd):
        try:
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            return result.returncode == 0
        except Exception:
            return False

    checks = {
        # 1.1.1.1 - Désactiver l'automontage
        "1.1.1.1_no_automount": run_cmd("systemctl is-enabled autofs | grep -q 'disabled'"),

        # 1.1.2 - Vérifier que /tmp est monté séparément
        "1.1.2_tmp_separate": run_cmd("mount | grep -E '\s/tmp\s' | grep -q 'nodev'"),

        # 1.4.1 - Activer AppArmor
        "1.4.1_apparmor_enabled": run_cmd("aa-status | grep -q 'profiles are loaded'"),

        # 2.2.1.3 - Interdire le login root SSH
        "2.2.1.3_no_ssh_root_login": run_cmd("grep -E '^PermitRootLogin\s+no' /etc/ssh/sshd_config"),

        # 3.1.1 - Vérifier les permissions de /etc/passwd
        "3.1.1_passwd_permissions": run_cmd("stat -c %a /etc/passwd | grep -qE '^6[0-4][0-4]$'"),

        # 3.3.4 - Alerte sur tentatives d'accès root échouées
        "3.3.4_failed_root_login": run_cmd("grep -q 'authentication failure.*user=root' /var/log/auth.log"),

        # 4.1.1.1 - Configurer auditd
        "4.1.1.1_auditd_installed": run_cmd("dpkg -s auditd | grep -q 'Status: install ok installed'"),

        # 5.3.1 - Définir les politiques de mot de passe
        "5.3.1_password_policies": run_cmd("grep -Eq '^PASS_MAX_DAYS\s+[0-9]{2,}' /etc/login.defs"),

        # 6.1.2 - Vérifier les fichiers UID 0
        "6.1.2_only_root_uid0": run_cmd("awk -F: '($3 == 0) { print $1 }' /etc/passwd | grep -xq 'root'"),

        # 6.2.1 - Vérifier les comptes sans mot de passe
        "6.2.1_no_empty_passwords": run_cmd("grep -E '^([^:]+:){1}!?:' /etc/shadow | wc -l | grep -q '^0$'"),
    }

    return checks