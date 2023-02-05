from pathlib import Path

# Create file if it doesn't exist
def file_exist(name):
    file = Path(name)
    file.touch(exist_ok=True)

def admin_check(ctx):
    file_exist('Admin.txt')
    with open('Admin.txt', 'r') as admin_file:
        for admin in admin_file.readlines():
            if str(ctx.message.author.id) == str(admin)[:-1]:
                return True
        return False