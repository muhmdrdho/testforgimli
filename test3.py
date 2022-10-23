import pygimli 
import mpld3
import streamlit as st
from pygimli.physics import ert 
import matplotlib.pyplot as plt 
import streamlit.components.v1 as components 

uploaded_file = st.file_uploader('choose')
if uploaded_file is not None:
    df = uploaded_file.name
    data = ert.load(df)
    data['k'] = ert.createGeometricFactors(data, numerical=True)

    ###############################################################################
    # We initialize the ERTManager for further steps and eventually inversion.
    mgr = ert.ERTManager(sr=False)

    ###############################################################################
    # It might be interesting to see the topography effect, i.e the ratio between
    # the numerically computed geometry factor and the analytical formula
    k0 = ert.createGeometricFactors(data)
    ert.showData(data, vals=k0/data['k'], label='Topography effect')

    ###############################################################################
    # The data container has no apparent resistivities (token field 'rhoa') yet.
    # We can let the Manager fix this later for us (as we now have the 'k' field),
    # or we do it manually.
    mgr.checkData(data)
    print(data)

    ###############################################################################
    # The data container does not necessarily contain data errors data errors
    # (token field 'err'), requiring us to enter data errors. We can let the
    # manager guess some defaults for us automaticly or set them manually
    data['err'] = ert.estimateError(data, absoluteUError=5e-5, relativeError=0.03)
    # or manually:
    # data['err'] = data_errors  # somehow
    ert.show(data, data['err']*100)

    ###############################################################################
    # Now the data have all necessary fields ('rhoa', 'err' and 'k') so we can run
    # the inversion. The inversion mesh will be created with some optional values
    # for the parametric mesh generation.
    #
    mod = mgr.invert(data, lam=10, verbose=True,
                    paraDX=0.3, paraMaxCellSize=10, paraDepth=20, quality=33.6)



    ###############################################################################
    # We can view the resulting model in the usual way.

    # np.testing.assert_approx_equal(ert.inv.chi2(), 1.10883, significant=3)

    ###############################################################################
    # Or just plot the model only using your own options.

    meshPD = pygimli.Mesh(mgr.paraDomain)
    modelPD = mgr.paraModel(mod)
    pygimli.show(mgr.paraDomain, modelPD, label='Model', cMap='Spectral_r', logScale=True, cMin=5, cMax=4000)
    fig, ax1 = plt.subplots(1,1)

    pygimli.show(meshPD, mod, ax=ax1, hold=True, cMap="Spectral_r", logScale=True, orientation="horizontal", cMin=5, cMax=4000)
    labels = ["True model"]
    for ax, label in zip([ax1], labels):
        ax.set_xlim(mgr.paraDomain.xmin(), mgr.paraDomain.xmax())
        ax.set_ylim(mgr.paraDomain.ymin(), mgr.paraDomain.ymax())
        ax.set_title(label)

    fig_html = mpld3.fig_to_html(fig)
    components.html(fig_html, height=600)
    
    
