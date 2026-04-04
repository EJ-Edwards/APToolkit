import textwrap


TOS_TEXT = """\
Terms of Service (TOS)

1. By using this software, you agree to be bound by these Terms of Service
   and all applicable laws and regulations. If you do not agree with any of
   these terms, you are prohibited from using or accessing this software.

2. You agree to use this software only for lawful purposes and in a way that
   does not infringe the rights of, restrict, or inhibit anyone else's use
   and enjoyment of the software. Prohibited behavior includes harassing or
   causing distress or inconvenience to any other user, transmitting obscene
   or offensive content, or disrupting the normal flow of dialogue within
   the software.

3. Whatever you do with this software, you are responsible for your actions. The
    developers and distributors of this software are not liable for any damage or
    loss that may occur as a result of using this software, including but not
    limited to direct, indirect, incidental, punitive, and consequential damages.
"""


def print_tos():
    """Display the TOS and require acceptance before continuing."""
    print(TOS_TEXT)
    agreed = input("Do you accept the Terms of Service? (yes/no): ").strip().lower()
    if agreed in ("yes", "y"):
        print("Thank you for accepting the Terms of Service. You may now use the software.")
        return True
    else:
        print("You must accept the Terms of Service to use this software. Exiting.")
        exit(0)


if __name__ == "__main__":
    print_tos()