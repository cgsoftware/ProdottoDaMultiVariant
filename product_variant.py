# -*- encoding: utf-8 -*-
from osv import fields, osv

import wizard
import decimal_precision as dp
import pooler
import time
from tools.translate import _
from osv import osv, fields
from tools.translate import _
import tools
import base64
from tempfile import TemporaryFile
from osv import osv, fields




class crea_articolo(osv.osv_memory):
    _name = 'crea.articolo'
    _description = 'Crea un articolo partendo dalle sue varianti definite '
    _columns = {
                'name': fields.many2one('product.template', 'Modello', required=True),
                'elenco_varianti':fields.one2many('crea.articolo.righe', 'testa', 'Righe Varianti Utilizzabili'),
                'marchio_id':fields.many2one('marchio.marchio', 'Marca', required=True),
                'adhoc_code': fields.char('Cod.Art.Ad-Hoc', size=15),
         }
    
    def _get_modello(self, cr, uid, context=None):
      #  import pdb;pdb.set_trace()
        Modello = self.pool.get('stock.move')
        if context is None:
            context = {}              
        ids = context.get('active_ids', [])
        if ids:
            return ids[0]
        else:
            return None

    
    
    _defaults = {
                # 'name':_get_modello
                }
    
    def onchange_modello(self, cr, uid, ids, name):
       # import pdb;pdb.set_trace()
        v = {}
        vals = {
                'name':name,
                }
        # id_art = self.create(cr, uid, vals, {})
        param = [('product_tmpl_id', '=', name)]
        ids_dimension = self.pool.get("product.variant.dimension.type").search(cr, uid, param)
        if ids_dimension:
            elenco_varianti = []
            for id_dim in ids_dimension:
                desc = self.pool.get("product.variant.dimension.type").browse(cr, uid, [id_dim])[0].desc_type
                elenco_varianti.append({'Dimensione_id':id_dim, 'desc_type':desc, 'valore_id': None})
            v = {'name':name, 'elenco_varianti':elenco_varianti}
                
        #Dimension_ids 
        return {'value':v}
    
    def crea_articolo(self, cr, uid, ids, context=None):
        #import pdb;pdb.set_trace()
        car_art = self.browse(cr, uid, ids)[0]
        Template = car_art.name
        codice_product = Template.codice_template
        extra_prezzo = 0
        desvar = ''
        lista_variant_value = []
        first = True
        for variante in car_art.elenco_varianti:
         if variante.valore_id:  ## sole se ha assegnato un codice alla variante
            codice_product = codice_product + "-" + variante.valore_id.name
            if first:
                first = False
            else:
                desvar = desvar + "-"
            des_var = desvar + variante.Dimensione_id.name + ":" + variante.valore_id.name
            extra_prezzo = extra_prezzo + variante.valore_id.price_extra
            lista_variant_value.append(variante.valore_id.id)
        #import pdb;pdb.set_trace()
        Prodotto = {
                    'product_tmpl_id':car_art.name.id,
                    'dimension_value_ids': [(6, 0, tuple(lista_variant_value))],
                    'default_code':codice_product + "-" + car_art.marchio_id.name,
                    'marchio_ids':car_art.marchio_id.id,
                    'price_extra':extra_prezzo,
                    'production_conai_peso':Template.production_peso,
                    'peso_prod':Template.production_peso,
                    'adhoc_code':car_art.adhoc_code,


                    }
        id_Articolo = self.pool.get('product.product').create(cr, uid, Prodotto, {})
        #import pdb;pdb.set_trace()
        # Articolo = self.pool.get('product.product').browse(cr, uid, [id_Articolo])
        #import pdb;pdb.set_trace()
        ''' MEMENTANEAMENTE IN COMMENTO IN MODO CHE LA CREAZIONE DELLA DISTINTA ABBIA UN ULTERIORE 
        #PASSAGGIO IN WIZARD E CHE LA GENERAZIONE DELLA DISTINTA A WIZARD  POSSA ESSERE LANCIATA SEPARATAMENTE
        if id_Articolo:
		Crea = self.pool.get('crea.distinta').onchange_articolo(cr, uid, ids, id_Articolo)
		if Crea:
        		id_crea = self.pool.get('crea.distinta').create(cr, uid, Crea , {})
       			ok = self.pool.get('crea.distinta').genera(cr, uid, [id_crea], context=None)
        '''
        
        context.update({'active_ids':[id_Articolo]})
        return {
            'name': 'Genera Distinta Base',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crea.distinta',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }
        

        
        # return {'type': 'ir.actions.act_window_close'}
    
crea_articolo()


class crea_articolo_righe(osv.osv_memory):
    _name = 'crea.articolo.righe'
    _description = 'Dettaglio Varianti Sefinite '
    _columns = {
                'Dimensione_id': fields.many2one('product.variant.dimension.type', 'Dimensione', required=True, ondelete='cascade'),
                'desc_type':fields.related('Dimensione_id', 'desc_type', type='char', relation='rproduct.variant.dimension.type', string='Descrizione', store=True, readonly=True),
                'testa':fields.many2one('crea.articolo', 'Modello', required=True, ondelete='cascade', select=True,),
                'valore_id':fields.many2one('product.variant.dimension.value', 'Valore', required=False),
         }
    
    def onchange_valore(self, cr, uid, ids, name, elenco_varianti):
        #import pdb;pdb.set_trace()
        v = {}
        return {'value':v}

crea_articolo_righe()
