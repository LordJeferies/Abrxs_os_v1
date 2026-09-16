from pathlib import Path
from geometra.registry import RendererRegistry, CatalogRegistry
from geometra.compiler import compile_lienzo

ROOT = Path(__file__).resolve().parents[1]


def synthetic_project():
    return {
        'schemaVersion':'abrxos.document.v3',
        'documentType':'ABRXOS_CANONICAL_DOCUMENT',
        'projectId':'TEST_PROJECT',
        'title':'Test Project',
        'revision':{'id':'R1','number':1},
        'catalogVersions':{'xr':'R5','sfx':'1.0','motion':'1.0','captions':'2.0'},
        'extensions':{'xrDefinitions':[], 'sfxDefinitions':[]},
        'pieces':[
            {
                'id':'intro_1','canonicalId':'INTRO_1','type':'intro','title':'Intro Test','stage':'ALFA','workflowStatus':'PENDIENTE','source':'DEFAULT','included':True,
                'sourceRanges':[{'id':'SRC1','order':1,'start':100.0,'end':112.0,'text':'Source truth'}],
                'parts':[{'partId':'P1','role':'HOOK','text':'Source truth'}],
                'timeline':[
                    {'id':'AR1','track':'aroll','type':'aroll','label':'A-roll Hook','start':0.0,'end':12.0,'partId':'P1','text':'Source truth','speaker':'Amanda','timingMode':'locked_to_source'},
                    {'id':'XR1','track':'xr','type':'xr','label':'Sistema visual','xrFamily':'XR06','definitionId':'XR06','start':2.0,'end':8.0,'partId':'P1','function':'Explicar el sistema','timingMode':'free','states':[{'stateId':'S01','start':2.0,'end':5.0,'description':'Entrada del sistema','assetIds':['A01']},{'stateId':'S02','start':5.0,'end':8.0,'description':'Salida del sistema','assetIds':['A02']}], 'assets':[{'assetId':'A01','localId':'A01','description':'Libreta inicial','prompt':'Prompt libreta inicial','status':'pending_creation'},{'assetId':'A02','localId':'A02','description':'Libreta final','prompt':'Prompt libreta final','status':'created'}]},
                    {'id':'IMG1','track':'images','type':'image','label':'A01 · Libreta','start':2.0,'end':5.0,'parentId':'XR1','asset':{'assetId':'A01','description':'Libreta inicial','prompt':'Prompt libreta inicial','status':'pending_creation'},'timingMode':'follow_parent'},
                    {'id':'SFX1','track':'sfx','type':'sfx','label':'Soft hit','definitionId':'SFX_HIT_SOFT_01','start':5.0,'end':5.18,'sfx':{'name':'Soft hit','search':'soft hit','status':'pending_selection'},'timingMode':'free'},
                    {'id':'CAP1','track':'captions','type':'captions','label':'Source truth','text':'Source truth','start':0.0,'end':4.0,'partId':'P1','timingMode':'locked_to_source'}
                ],
                'schedule':{'date':'','time':'','platforms':[]}
            },
            {
                'id':'c1','canonicalId':'C1','type':'carousel','title':'Carousel Test','stage':'ALFA','workflowStatus':'LISTO','included':True,
                'timeline':[], 'sourceRanges':[], 'parts':[], 'schedule':{'date':'','time':'','platforms':[]},
                'staticProduction':{'mode':'storyboard','itemLabel':'Slide','itemLabelPlural':'Slides','items':[{'itemId':'S01','index':1,'function':'HOOK','headline':'Slide One','body':'Body one','text':'Slide One\nBody one','visual':{'description':'Visual one','prompt':'Prompt one'}},{'itemId':'S02','index':2,'function':'VALUE','headline':'Slide Two','body':'Body two','text':'Slide Two\nBody two','visual':{'description':'Visual two','prompt':'Prompt two'}}], 'copy':{'text':'Carousel copy'}}
            }
        ]
    }


def compile_test_html(renderer='joc-classic'):
    rr=RendererRegistry(ROOT/'renderers'); cr=CatalogRegistry(ROOT/'catalogs')
    p=synthetic_project()
    return compile_lienzo(p,renderer,[],f'Test {renderer}','dark',rr,cr,ROOT)
