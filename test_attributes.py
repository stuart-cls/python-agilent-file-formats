from agilent import agilentImage, agilentMosaic

ai = agilentImage("var/fpa_refl_vi.pb.seq", MAT=False)
am = agilentMosaic("var/2017-11-10 4X-25X/2017-11-10 4X-25X.dms", MAT=False)

for a in [ai, am]:
    assert a.data.shape[2] == len(a.info['wavenumbers'])
    assert a.wavenumbers == a.info['wavenumbers']
    assert a.width == a.data.shape[0]
    assert a.height == a.data.shape[1]
    assert a.filename in ["var/fpa_refl_vi.pb.bsp",
                          "var/2017-11-10 4X-25X/2017-11-10 4X-25X.dms" ]
    assert a.acqdate in ["Friday, November 10, 2017 15:22:29",
                         "Friday, November 10, 2017 13:46:28"]
