import os
import certifi
from modules.shared import cmd_opts

def trust_cert(cert):
	"""given path to a certificate, add it to the trust store. Return 1 on success, -1 if already added"""
	with open(cert, 'r') as infile:
		local_cert = infile.read()

	bundle_path = certifi.where()
	with open(bundle_path, 'r+') as ca_bundle:
		orig = ca_bundle.read()

		# check that we have not already appended the certificate to the certifi trust store/CA bundle
		if orig.find(local_cert) == -1:
			temp_path = bundle_path + ".temp"
			temp = open(temp_path, 'w')

			# prepend instead of append because the first matching cert takes priority,
			# and we do not want to collide with any of our previous additions
			temp.write("\n#\n#\n#\n# ADDED BY AUTOMATIC1111 WEBUI\n#\n#\n#\n")
			temp.write(local_cert)
			temp.write(orig)

			temp.close()
			os.remove(bundle_path)
			os.rename(temp_path, bundle_path)
			return -1
		else:
			return 1
	ca_bundle.close()
	infile.close()



if not cmd_opts.self_sign:
	import certipie
	cmd_opts.tls_keyfile = "./webui.key"
	cmd_opts.tls_certfile = "./webui.cert"

	if not os.path.exists(cmd_opts.tls_certfile) and not os.path.exists(cmd_opts.tls_keyfile):
		privkey = certipie.create_private_key(filename=cmd_opts.tls_keyfile)
		certipie.create_auto_certificate(
			filename=cmd_opts.tls_certfile,
			private_key=privkey,
			# it seems like requests prioritizes CN despite CN being deprecated by SAN's?
			# localhost is already picked as the cert common name by default through constructor
			common_name=cmd_opts.server_name if cmd_opts.server_name else "localhost",
			alternative_names=None,
			organization="AUTOMATIC1111 Web-UI",
			country='TD',
			state_or_province="fake state",
			city="fake city",
		)
		print("Generated new key/cert pair")
	else:
		print("Default key/cert pair was already generated by webui")
else:
	try:
		if not os.path.exists(cmd_opts.tls_keyfile):
			print(f"Invalid path to TLS certfile: '{cmd_opts.tls_keyfile}'")
		if not os.path.exists(cmd_opts.tls_certfile):
			print(f"Invalid path to TLS certfile: '{cmd_opts.tls_certfile}'")
	except TypeError as e:
		cmd_opts.tls_keyfile = cmd_opts.tls_certfile = None
		print("TLS components missing or invalid.")
		raise e

trusted = trust_cert(cmd_opts.tls_certfile)
if trusted == 1:
	print('Certificate was found in trust store ✔️')
else:
	print('Certificate trust store updated')