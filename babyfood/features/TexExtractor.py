import os, tempfile
import xml.etree.ElementTree as ET

texTemplate = '''\\documentclass{article}
%s
\\begin{document}
\\thispagestyle{empty}
%s
\\end{document}"
'''

class TexFeature(object):
	def setText(self, textToRender, headers=""):
		# Create the TeX file
		d = tempfile.mkdtemp()
		texFile = tempfile.NamedTemporaryFile(mode='w+', suffix=".tex", dir=d)
		texFile.write(texTemplate % (headers, textToRender))
		texFile.flush()

		# TeX -> pdf file
		os.system("pdflatex -output-directory %s %s" % (d, texFile.name))

		reSuffix = lambda filepath, newSuffix: os.path.splitext(filepath)[0] + "." + newSuffix

		# pdf file -> svg file
		texPath = os.path.join(d, texFile.name)
		pdfPath = reSuffix(texPath, "pdf")
		svgPath = reSuffix(texPath, "svg")

		call = "pdf2svg %s %s" % (pdfPath, svgPath)
		print(call)
		os.system(call)

		# Load the raw svg data
		svgTree = ET.parse(svgPath)

		for element in svgTree.getroot():
			print(element)

		symbols = svgTree.findall("./svg")
		strikes = svgTree.findall("use")

		print("Symbols:")
		for s in symbols:
			print(s.attrib)

		print()
		print("Strikes:")
		for s in strikes:
			print(s.attrib)


if __name__ == "__main__":
	tf = TexFeature()
	tf.setText("Hello! \n\n $3 + 1$")