#core/execution/ffuf_command.py

def build_ffuf_command(url, wordlist, output_file, profile):
    cmd = [
        "ffuf",
        "-u", url,
        "-w", wordlist,
        "-t", str(profile.threads),
        "-mc", ",".join(map(str, profile.status_codes)),
        "-of", "json",
        "-o", output_file,
        "-timeout", str(profile.timeout),
    ]

    if profile.filter_size_zero:
        cmd += ["-fs", "0"]

    return cmd
