# Factura.com Python v1.1
This is a wrapper for Factura.com's services.

# Installation

```bash
pip install facturacom
```

# Quickstart

To quickly test the library we recommend you try listing all your
CFDIs currently on the servers.

```python
import facturacom

facturacom.API.key = 'YOUR API KEY'
facturacom.API.secret_key = 'YOUR SECRET KEY'
facturacom.API.mode = 'SANDBOX'  # or PRODUCTION

all_cfdis = facturacom.CFDI33.list()  # list all cfdis

for cfdi in all_cfdis:
    print('id: %s' % cfdi.uid)
    print('total: %s\n' % cfdi.uid)
```

## Listing CFDIs

```python
import facturacom

facturacom.API.key = 'YOUR API KEY'
facturacom.API.secret_key = 'YOUR SECRET KEY'
facturacom.API.mode = 'SANDBOX'  # or PRODUCTION

all_cfdis = facturacom.CFDI33.list()  # list all cfdis

cfdis_january = facturacom.CFDI33.list({  # list only january's cfdis
    'month': 1
})
```