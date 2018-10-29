from os.path import join
import subprocess

template = r'''\documentclass[preview]{{standalone}}
            \usepackage{{booktabs}}
            \begin{{document}}
            {}
            \end{{document}}
            '''


def datframe_to_png(df, filename, outputdir):

    filepath = join(outputdir, filename)

    # write to latex
    with open(filepath+'.tex', 'w') as f:
        latex = df.to_latex()
        f.write(template.format(latex))

    # convert latex to PDF
    subprocess.call(['pdflatex',
                     '-output-directory', outputdir,
                     filepath+'.tex'])

    # convert PDF to PNG
    subprocess.call(['sips', '-s', 'format', 'png', filepath+'.pdf', '--out', filepath+'.png'])
