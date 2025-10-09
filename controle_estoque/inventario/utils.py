from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
from django.conf import settings
import base64

# --- INÍCIO DA ADAPTAÇÃO ---
# Força o matplotlib a usar um modo "não-visual" para evitar erros no servidor
import matplotlib
matplotlib.use('Agg')
# --- FIM DA ADAPTAÇÃO ---

import matplotlib.pyplot as plt

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    
    # Set encoding to handle Portuguese characters
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, 
                           encoding='UTF-8',
                           link_callback=link_callback)
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def generate_pie_chart(data, title):
    """Gera um gráfico de pizza e retorna como uma imagem base64."""
    if not data:
        return None

    labels = [item['produto__nome'] for item in data]
    sizes = [item['total_quantidade'] for item in data]

    fig, ax = plt.subplots(figsize=(6, 4)) # Ajusta o tamanho da figura
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
    ax.axis('equal')  # Garante que a pizza seja um círculo.
    plt.title(title, fontsize=12)

    # Salva o gráfico em um buffer de memória
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)

    # Codifica a imagem em base64
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # Use short variable names
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATIC_ROOT    # Typically /some/path/project/static/
    mUrl = settings.MEDIA_URL       # Typically /media/
    mRoot = settings.MEDIA_ROOT     # Typically /some/path/project/media/

    # Convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (i.e., http://some.tld/foo.png)

    # Make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path