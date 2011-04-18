import re
from pychess.Utils.const import *
import time
import math
from pychess.System import conf

elemExpr = re.compile(r"([a-zA-Z])\s*([0-9\.,\s]*)\s+")
spaceExpr = re.compile(r"[\s,]+")

l = []

def parse(n, psize):
    yield "def f(c):"
    s = psize/size
    for cmd, points in n:
        pstr = ",".join(str(p*s) for p in points)
        if cmd == "M":
            yield "c.rel_move_to(%s)" % pstr
        elif cmd == "L":
            yield "c.rel_line_to(%s)" % pstr
        else:
            yield "c.rel_curve_to(%s)" % pstr
            
# This has double speed at drawing, but when generating new functions, it
# takes about ten times longer.
def drawPiece3 (piece, cc, x, y, psize):
    cc.save()
    cc.move_to(x,y)
    
    if not psize in parsedPieces[piece.color][piece.sign]:
        exec("\n    ".join(parse(parsedPieces[piece.color][piece.sign][size],psize)))
        parsedPieces[piece.color][piece.sign][psize] = f
    
    cc.fill()
    cc.restore()

def drawPieceReal (piece, cc, psize):
    
    # Do the actual drawing to the Cairo context
    for cmd, points in parsedPieces[piece.color][piece.sign][psize]:
        if cmd == 'M':
            cc.rel_move_to(*points)
        elif cmd == 'L':
            cc.rel_line_to(*points)
        else:
            cc.rel_curve_to(*points)

def drawPiece (piece, cc, x, y, psize):
    cc.save()
    cc.move_to(x,y)
    
    if not psize in parsedPieces[piece.color][piece.sign]:
        list = [(cmd, [(p*psize/size) for p in points])
                for cmd, points in parsedPieces[piece.color][piece.sign][size]]
        parsedPieces[piece.color][piece.sign][psize] = list
    
    drawPieceReal (piece, cc, psize)
    cc.fill()
    cc.restore()

# This version has proven itself nearly three times as slow as the "draw each time" method. At least when drawing one path only. Might be useful when drawing svg    
import cairo
def drawPiece2 (piece, cc, x, y, psize):
    if not piece in surfaceCache:
        s = cc.get_target().create_similar(cairo.CONTENT_COLOR_ALPHA, int(size), int(size))
        ctx = cairo.Context(s)
        ctx.move_to(0,0)
        drawPieceReal (piece, ctx, size)
        ctx.set_source_rgb(0,0,0)
        ctx.fill()
        surfaceCache[piece] = s
    
    cc.save()
    
    cc.set_source_rgb(0,0,0)
    cc.scale(psize/size, psize/size)
    cc.translate(x*size/psize, y*size/psize)
    cc.rectangle (0, 0, int(size), int(size))
    
    # TODO: DOes this give any performance boost?
    # From cairo thread:
    # Or paint() instead of fill().  fill() needs a path, so you should do a
    # rectangle() first.
    
    
    cc.set_source_surface(surfaceCache[piece], 0, 0)
    cc.fill()
    cc.restore()
surfaceCache = {}

size = 800.0
pieces = {
    BLACK: {
        KING: "M 653.57940,730.65870 L 671.57940,613.65870 C 725.57940,577.65870 797.57940,514.65870 797.57940,397.65870 C 797.57940,325.65870 734.57940,280.65870 662.57940,280.65870 C 590.57940,280.65870 509.57940,334.65870 509.57940,334.65870 C 509.57940,334.65870 554.57940,190.65870 428.57940,154.65870 L 428.57940,118.65870 L 482.57940,118.65870 L 482.57940,64.658690 L 428.57940,64.658690 L 428.57940,10.658690 L 374.57940,10.658690 L 374.57940,64.658690 L 320.57940,64.658690 L 320.57940,118.65870 L 374.57940,118.65870 L 374.57940,154.65870 C 248.57940,190.65870 293.57940,334.65870 293.57940,334.65870 C 293.57940,334.65870 212.57940,280.65870 140.57940,280.65870 C 68.579380,280.65870 5.5793840,325.65870 5.5793840,397.65870 C 5.5793840,514.65870 77.579380,577.65870 131.57940,613.65870 L 149.57940,730.65870 C 158.57940,757.65870 221.57940,793.65870 401.57940,793.65870 C 581.57940,793.65870 644.57940,757.65870 653.57940,730.65870 z M 374.57940,541.65870 C 329.57940,541.65870 212.57940,550.65870 167.57940,568.65870 C 113.57940,541.65870 59.579380,496.65870 59.579380,406.65870 C 59.579380,352.65870 86.579380,334.65870 149.57940,334.65870 C 212.57940,334.65870 356.57940,397.65870 374.57940,541.65870 z M 428.57940,541.65870 C 446.57940,397.65870 590.57940,334.65870 662.57940,334.65870 C 716.57940,334.65870 743.57940,352.65870 743.57940,406.65870 C 743.57940,496.65870 689.57940,541.65870 635.57940,568.65870 C 590.57940,550.65870 473.57940,541.65870 428.57940,541.65870 z M 617.57940,667.65870 L 608.57940,705.90870 C 437.57940,678.90870 365.57940,678.90870 194.57940,705.90870 L 185.57940,667.65870 C 365.57940,640.65870 437.57940,640.65870 617.57940,667.65870 z M 464.57940,514.65870 C 527.57940,514.65870 581.57940,523.65870 635.57940,541.65870 C 707.57940,487.65870 716.57940,442.65870 716.57940,406.65870 C 716.57940,379.65870 698.57940,361.65870 662.57940,361.65870 C 554.57940,361.65670 473.57940,451.65870 464.57940,514.65870 z M 338.57940,514.65870 C 329.57940,451.65870 239.57940,361.65670 140.57940,361.65870 C 104.57940,361.65870 86.579380,388.65870 86.579380,415.65870 C 86.579380,442.65870 95.579380,487.65870 167.57940,541.65870 C 221.57940,523.65870 275.57940,514.65870 338.57940,514.65870 z ",
        QUEEN: "M 617.12310,626.00950 C 617.12310,599.00950 627.77310,557.68550 671.12310,536.00950 C 689.12310,527.00950 689.12310,509.00950 689.12310,500.00950 C 689.12310,471.54950 743.12310,203.00950 743.12310,203.00950 C 779.62510,198.74750 796.96610,170.47750 796.96610,144.34650 C 796.96610,112.98940 772.26810,85.907430 738.52810,85.907430 C 710.73310,85.907430 680.56310,109.18740 679.85110,143.63450 C 679.66510,152.63250 681.03910,169.05250 697.43010,186.15650 L 590.12310,392.00950 L 590.12310,158.00950 C 619.03410,151.95050 636.85210,127.48250 636.85210,99.687430 C 636.85210,69.517430 610.72110,42.199430 577.93710,42.199430 C 544.44210,42.199430 519.27910,70.470430 519.73610,102.06340 C 519.97310,118.45540 527.57510,136.03450 545.12410,149.00950 L 464.12410,383.00950 L 428.12410,131.00950 C 452.74310,117.03040 459.86810,97.075430 459.86810,80.208430 C 459.86810,41.011430 428.74910,20.581430 401.19210,20.818430 C 371.26010,21.076430 342.75310,46.950430 342.75310,77.120430 C 342.75310,107.05240 359.14410,122.73150 374.12410,131.00950 L 338.12410,383.00950 L 257.12410,149.00950 C 275.75910,134.13450 282.17310,119.64340 282.17310,98.976430 C 282.17310,77.833430 264.35910,42.199430 223.25910,42.199430 C 190.47610,42.199430 165.29410,70.944430 165.29410,99.926430 C 165.29410,134.84850 190.23910,153.37750 212.12410,158.01050 L 212.12410,392.01050 L 104.12410,185.01050 C 117.78210,170.95350 120.15710,154.06050 120.15710,145.06050 C 120.15710,114.41440 97.114060,85.807430 59.124060,86.010430 C 33.925060,86.146430 3.4010650,109.06240 3.0420650,145.06050 C 2.8040650,168.81650 20.858060,200.88650 59.124060,203.01050 C 59.124060,203.01050 113.12410,473.01050 113.12410,500.01050 C 113.12410,509.01150 113.12410,527.01050 131.12410,536.01050 C 167.12410,554.01150 185.12410,599.01050 185.12410,626.01050 C 185.12410,662.01150 158.12410,698.01150 158.12410,707.01150 C 158.12410,752.01050 320.12410,779.01150 401.12410,778.99150 C 473.12410,778.97350 644.12410,752.01050 644.12410,707.01050 C 644.12410,698.01050 617.12410,671.01050 617.12410,626.01050 L 617.12310,626.00950 z M 594.55210,537.12950 C 583.21810,553.12950 581.21810,558.46250 576.55210,575.12950 C 487.21810,553.79650 327.21810,547.79650 225.88510,575.79650 C 221.21710,557.79650 219.21710,550.46250 208.55110,537.12950 C 325.21710,508.46250 479.21710,506.46250 594.55110,537.12950 L 594.55210,537.12950 z M 570.55210,663.79650 C 555.88510,674.46250 551.21810,682.46250 542.55210,693.79650 C 434.55210,677.12950 363.88410,674.46250 255.21810,693.12950 C 246.55210,679.79650 241.88610,673.12950 229.21810,663.79650 C 341.88610,634.46250 457.88610,644.46250 570.55210,663.79650 L 570.55210,663.79650 z ",
        ROOK: "M 232.94440,519.29360 L 124.94440,627.29360 L 124.94440,762.29360 L 682.94440,762.29360 L 682.94440,627.29360 L 574.94440,519.29360 L 574.94440,303.29360 L 682.94440,231.29360 L 682.94440,51.293580 L 520.94440,51.293580 L 520.94440,123.29360 L 484.94440,123.29360 L 484.94440,51.293580 L 322.94440,51.293580 L 322.94440,123.29360 L 286.94440,123.29360 L 286.94440,51.293580 L 124.94440,51.293580 L 124.94440,231.29360 L 232.94440,303.29360 L 232.94440,519.29360 z M 268.94440,321.29360 L 268.94440,285.29360 L 538.94440,285.29360 L 538.94440,321.29360 L 268.94440,321.29360 z M 268.94440,537.29360 L 268.94440,501.29360 L 538.94440,501.29360 L 538.94440,537.29360 L 268.94440,537.29360 z ",
        BISHOP: "M 491.69440,453.44430 L 500.69440,482.69430 C 464.69440,455.69430 338.69440,455.69430 302.69440,482.69430 L 311.69440,453.44430 C 332.69440,432.44430 470.69440,432.44430 491.69440,453.44430 z M 509.69440,518.69430 L 518.69440,545.69430 C 470.69440,521.69430 332.69440,521.69430 284.69440,545.69430 L 293.69440,518.69430 C 338.69440,491.69430 464.69440,491.69430 509.69440,518.69430 z M 797.69440,653.69430 C 797.69440,653.69430 752.69440,635.69430 689.69440,626.69430 C 652.95940,621.44630 599.69440,635.69430 554.69440,626.69430 C 518.69440,617.69430 482.69440,599.69430 482.69440,599.69430 L 572.69440,554.69430 L 545.69440,473.69430 C 545.69440,473.69430 608.69440,446.69430 608.69440,365.69430 C 608.69440,302.69430 563.69440,230.69430 500.69440,194.69430 C 455.13040,168.65830 446.69440,149.69430 446.69440,149.69430 C 446.69440,149.69430 482.69440,131.69430 482.69440,86.694330 C 482.69440,50.694330 455.69440,5.6943260 401.69440,5.6943260 C 347.69440,5.6943260 320.69440,50.694330 320.69440,86.694330 C 320.69440,131.69430 356.69440,149.69430 356.69440,149.69430 C 356.69440,149.69430 348.25840,168.65830 302.69440,194.69430 C 239.69440,230.69430 194.69440,302.69430 194.69440,365.69430 C 194.69440,446.69430 257.69440,473.69430 257.69440,473.69430 L 230.69440,554.69430 L 320.69440,599.69430 C 320.69440,599.69430 284.69440,617.69430 248.69440,626.69430 C 204.17340,637.82430 146.99540,621.93730 113.69440,626.69430 C 50.694360,635.69430 5.6943640,653.69430 5.6943640,653.69430 L 50.694360,797.69430 C 113.69440,779.69430 122.69440,779.69430 176.69440,770.69430 C 209.78640,765.17930 291.51040,774.42230 329.69440,761.69430 C 383.69440,743.69430 401.69440,716.69430 401.69440,716.69430 C 401.69440,716.69430 419.69440,743.69430 473.69440,761.69430 C 511.87840,774.42230 598.40740,767.15830 626.69440,770.69430 C 681.01640,777.48430 752.69440,797.69430 752.69440,797.69430 L 797.69440,653.69430 L 797.69440,653.69430 z M 428.69440,392.69430 L 374.69440,392.69430 L 374.69440,356.69430 L 338.69440,356.69430 L 338.69440,302.69430 L 374.69440,302.69430 L 374.69440,266.69430 L 428.69440,266.69430 L 428.69440,302.69430 L 464.69440,302.69430 L 464.69440,356.69430 L 428.69440,356.69430 L 428.69440,392.69430 z ",
        KNIGHT: "M 84.310370,730.48460 L 564.28850,729.48460 C 563.97550,600.58860 477.97550,556.58860 485.00550,477.74860 L 587.06050,552.58860 C 611.11150,581.44960 637.05150,594.72560 657.36750,594.91660 C 671.53450,595.04960 633.37050,547.08060 627.37050,536.08060 C 653.37050,535.08060 689.37050,585.08060 718.38750,574.11560 C 739.54850,566.12160 754.01750,540.22060 753.06850,502.24260 C 751.70850,447.81260 690.47450,367.52960 667.34250,266.83660 C 641.48850,160.69960 611.91250,147.09260 595.58450,141.64850 L 595.22350,64.085560 L 513.57950,123.95850 L 467.31450,43.675570 L 421.04950,138.92750 C 260.48350,91.300560 89.752370,428.40260 84.309370,730.48460 L 84.310370,730.48460 z M 125.87840,697.92560 C 125.87840,436.61260 289.76850,168.92760 381.72850,167.10560 C 399.37150,167.41260 415.37150,173.41260 415.32750,179.85360 C 415.24050,192.63260 399.02750,197.15260 379.90750,197.15260 C 307.97850,199.88460 158.65640,453.00260 156.83540,695.19560 C 156.83540,713.40460 127.70040,712.49460 125.87940,697.92560 L 125.87840,697.92560 z M 678.74350,471.34160 C 684.09050,477.57960 689.68150,486.16560 689.86350,492.19160 C 690.09450,499.83660 684.07150,505.86160 678.28050,503.54360 C 672.48850,501.22760 665.53850,488.25260 660.90550,485.70560 C 656.27250,483.15660 642.14050,481.30360 642.37250,474.81660 C 642.60450,468.32960 652.10250,462.53760 657.66250,462.76960 C 663.22250,463.00160 675.96450,468.09760 678.74450,471.34160 L 678.74350,471.34160 z M 520.98750,218.08460 C 534.62350,223.81160 559.71450,235.26460 577.44150,255.99260 C 594.62350,278.90060 595.98650,304.80860 596.53150,323.35560 C 566.80450,326.90060 541.87450,318.25160 529.44150,290.90060 C 521.25950,272.90060 520.98650,239.62960 520.98650,218.08460 L 520.98750,218.08460 z ",
        PAWN: "M 688.02380,750.97630 L 688.02380,624.97630 C 688.02380,579.97630 661.62380,452.47630 553.02380,408.97630 C 598.02380,354.97630 607.02380,255.97630 517.02380,192.97630 C 544.02380,156.97630 517.02380,30.976220 409.02380,30.976220 C 301.02380,30.976220 274.02380,156.97630 301.02380,192.97630 C 211.02380,255.97630 220.02380,354.97630 265.02380,408.97630 C 157.02380,453.97630 130.02380,579.97630 130.02380,624.97630 L 130.02380,750.97630 L 688.02380,750.97630 z "
    },
    WHITE: {
        KING: "M 648.50000,730.65870 L 666.50000,613.65870 C 720.50000,577.65870 792.50000,514.65870 792.50000,397.65870 C 792.50000,325.65870 729.50000,280.65870 657.50000,280.65870 C 585.50000,280.65870 504.50000,334.65870 504.50000,334.65870 C 504.50000,334.65870 549.50000,190.65870 423.50000,154.65870 L 423.50000,118.65870 L 477.50000,118.65870 L 477.50000,64.658690 L 423.50000,64.658690 L 423.50000,10.658690 L 369.50000,10.658690 L 369.50000,64.658690 L 315.50000,64.658690 L 315.50000,118.65870 L 369.50000,118.65870 L 369.50000,154.65870 C 243.50000,190.65870 288.50000,334.65870 288.50000,334.65870 C 288.50000,334.65870 207.50000,280.65870 135.50000,280.65870 C 63.500000,280.65870 0.50000000,325.65870 0.50000000,397.65870 C 0.50000000,514.65870 72.500000,577.65870 126.50000,613.65870 L 144.50000,730.65870 C 153.50000,757.65870 216.50000,793.65870 396.50000,793.65870 C 576.50000,793.65870 639.50000,757.65870 648.50000,730.65870 z M 396.50000,451.65870 C 396.50000,451.65870 333.50000,343.65870 333.50000,280.65870 C 333.50000,217.65870 369.50000,208.65870 396.50000,208.65870 C 423.50000,208.65870 459.50000,226.65870 459.50000,280.65870 C 459.50000,334.65870 396.50000,451.65870 396.50000,451.65870 z M 369.50000,541.65870 C 324.50000,541.65870 207.50000,550.65870 162.50000,568.65870 C 108.50000,541.65870 54.500000,496.65870 54.500000,406.65870 C 54.500000,352.65870 81.500000,334.65870 144.50000,334.65870 C 207.50000,334.65870 351.50000,397.65870 369.50000,541.65870 z M 423.50000,541.65870 C 441.50000,397.65870 585.50000,334.65870 657.50000,334.65870 C 711.50000,334.65870 738.50000,352.65870 738.50000,406.65870 C 738.50000,496.65870 684.50000,541.65870 630.50000,568.65870 C 585.50000,550.65870 468.50000,541.65870 423.50000,541.65870 z M 612.50000,613.65870 L 603.50000,685.65870 C 432.50000,658.65870 360.50000,658.65870 189.50000,685.65870 L 180.50000,613.65870 C 360.50000,586.65870 432.50000,586.65870 612.50000,613.65870 z M 549.50000,730.65870 C 468.50000,748.65870 441.50000,748.65870 396.50000,748.65870 C 351.50000,748.65870 324.50000,748.65870 243.50000,730.65870 C 324.50000,712.65870 342.50000,712.65870 396.50000,712.65870 C 450.50000,712.65870 468.50000,712.65870 549.50000,730.65870 z ",
        QUEEN: "M 764.60380,143.65350 C 764.80680,155.66150 755.91880,166.72550 742.61880,166.56350 C 727.46980,166.37750 719.85480,154.92450 719.70980,144.57750 C 719.52480,131.46050 729.68780,121.66950 742.24980,121.66950 C 754.99780,121.66950 764.41980,132.75350 764.60380,143.65350 L 764.60380,143.65350 z M 619.66280,626.00950 C 619.66280,599.00950 630.31280,557.68550 673.66280,536.00950 C 691.66280,527.00950 691.66280,509.00950 691.66280,500.00950 C 691.66280,471.54950 745.66280,203.00950 745.66280,203.00950 C 782.16480,198.74750 799.50580,170.47750 799.50580,144.34650 C 799.50580,112.98950 774.80780,85.907570 741.06780,85.907570 C 713.27280,85.907570 683.10280,109.18750 682.39080,143.63450 C 682.20480,152.63250 683.57880,169.05250 699.96980,186.15650 L 592.66280,392.00950 L 592.66280,158.00950 C 621.57380,151.95050 639.39180,127.48250 639.39180,99.687540 C 639.39180,69.517570 613.26080,42.199570 580.47680,42.199570 C 546.98180,42.199570 521.81880,70.470570 522.27580,102.06350 C 522.51280,118.45550 530.11480,136.03450 547.66380,149.00950 L 466.66380,383.00950 L 430.66380,131.00950 C 455.28280,117.03050 462.40880,97.075540 462.40880,80.208570 C 462.40880,41.011570 431.28880,20.581570 403.73180,20.818570 C 373.79980,21.076570 345.29380,46.950570 345.29380,77.120570 C 345.29380,107.05250 361.68480,122.73150 376.66380,131.00950 L 340.66380,383.00950 L 259.66380,149.00950 C 278.29980,134.13450 284.71380,119.64350 284.71380,98.976540 C 284.71380,77.833570 266.89880,42.199570 225.79980,42.199570 C 193.01680,42.199570 167.83480,70.944570 167.83480,99.926540 C 167.83480,134.84850 192.77880,153.37750 214.66380,158.01050 L 214.66380,392.01050 L 106.66380,185.01050 C 120.32180,170.95350 122.69780,154.06050 122.69780,145.06050 C 122.69780,114.41450 99.654770,85.807570 61.663770,86.010570 C 36.464770,86.146570 5.9407760,109.06250 5.5817760,145.06050 C 5.3447760,168.81650 23.398770,200.88650 61.663770,203.01050 C 61.663770,203.01050 115.66380,473.01050 115.66380,500.01050 C 115.66380,509.01150 115.66380,527.01050 133.66380,536.01050 C 169.66380,554.01150 187.66380,599.01050 187.66380,626.01050 C 187.66380,662.01150 160.66380,698.01150 160.66380,707.01150 C 160.66380,752.01050 322.66380,779.01150 403.66380,778.99150 C 475.66380,778.97350 646.66380,752.01050 646.66380,707.01050 C 646.66380,698.01050 619.66380,671.01050 619.66380,626.01050 L 619.66280,626.00950 z M 87.606770,144.04950 C 87.809770,156.05650 78.921770,167.12050 65.621770,166.95850 C 50.472770,166.77350 42.857770,155.31950 42.712770,144.97350 C 42.527770,131.85650 52.690770,122.06450 65.252770,122.06450 C 78.000770,122.06450 87.422770,133.14950 87.606770,144.04950 z M 603.61080,99.656540 C 603.81380,111.66350 594.92580,122.72750 581.62580,122.56550 C 566.47680,122.38050 558.86180,110.92650 558.71680,100.58050 C 558.53180,87.463540 568.69480,77.671570 581.25680,77.671570 C 594.00480,77.671570 603.42680,88.756540 603.61080,99.656540 L 603.61080,99.656540 z M 426.61880,78.157570 C 426.82180,90.165540 417.93380,101.22950 404.63380,101.06750 C 389.48480,100.88150 381.86980,89.428540 381.72480,79.081570 C 381.53980,65.964570 391.70280,56.173570 404.26480,56.173570 C 417.01280,56.173570 426.43480,67.257570 426.61880,78.157570 z M 249.12780,100.65650 C 249.33080,112.66350 240.44280,123.72750 227.14280,123.56550 C 211.99380,123.38050 204.37880,111.92650 204.23380,101.58050 C 204.04880,88.463540 214.21180,78.671570 226.77380,78.671570 C 239.52180,78.671570 248.94380,89.756540 249.12780,100.65650 z M 578.63980,575.93450 C 569.63980,591.93450 563.63980,630.93450 573.63980,663.93450 C 467.97280,643.60050 338.63980,637.93450 231.63980,663.93450 C 238.63980,638.93450 240.63980,613.93450 227.63980,575.93450 C 320.63980,544.93450 515.63980,553.93450 578.63980,575.93450 L 578.63980,575.93450 z M 537.63980,707.93450 C 489.97280,725.93450 429.97280,726.26850 399.97280,726.26850 C 369.97280,726.26850 308.97280,723.93450 264.63980,708.93450 C 317.63980,697.93450 362.30680,695.60050 397.30680,695.60050 C 432.30680,695.60050 497.97280,700.26850 537.63980,707.93450 z M 210.32980,536.94050 C 210.32980,536.94050 205.66280,530.27350 200.99580,524.94050 C 210.32980,522.27350 232.99580,509.60650 244.32980,494.94050 C 291.66280,508.94050 316.32980,498.94050 350.99580,476.27350 C 384.32980,494.94050 417.66280,494.27350 458.99580,474.94050 C 486.32980,498.27350 515.66280,504.27350 559.66280,495.60650 C 576.32980,512.94050 586.99580,518.94050 604.32980,525.60650 L 596.32980,536.94050 C 454.32980,506.94050 358.99580,506.27350 210.32980,536.94050 L 210.32980,536.94050 z M 691.30580,290.55250 L 654.25080,486.80250 C 626.80380,493.20650 606.21880,481.76950 593.40980,465.30150 L 691.30580,290.55250 z M 553.20180,247.31050 L 550.98680,445.24750 C 523.09080,454.98950 508.03480,450.56150 487.66580,434.17750 L 553.20180,247.31050 z M 401.76580,233.14150 L 433.64780,429.30650 C 416.82180,441.26250 388.48180,443.47650 369.44080,428.74850 L 401.76580,233.14150 z M 252.98380,254.39550 L 318.96280,441.26250 C 304.35080,457.64650 279.55280,464.28750 255.64180,452.77550 L 252.98480,254.39550 L 252.98380,254.39550 z M 116.63980,294.93450 L 212.13980,463.43450 C 201.63980,481.43450 175.13980,492.43450 151.13980,485.43450 L 116.63980,294.93450 z ",
        ROOK: "M 227.86510,504.05560 L 119.86510,612.05560 L 119.86510,747.05560 L 677.86510,747.05560 L 677.86510,612.05560 L 569.86510,504.05560 L 569.86510,288.05560 L 677.86510,216.05560 L 677.86510,36.055570 L 515.86510,36.055570 L 515.86510,108.05560 L 479.86510,108.05560 L 479.86510,36.055570 L 317.86510,36.055570 L 317.86510,108.05560 L 281.86510,108.05560 L 281.86510,36.055570 L 119.86510,36.055570 L 119.86510,216.05560 L 227.86510,288.05560 L 227.86510,504.05560 z M 623.86510,90.055570 L 623.86510,180.05560 L 515.86510,252.05560 L 281.86510,252.05560 L 173.86510,180.05560 L 173.86510,90.055570 L 227.86510,90.055570 L 227.86510,162.05560 L 371.86510,162.05560 L 371.86510,90.055570 L 425.86510,90.055570 L 425.86510,162.05560 L 569.86510,162.05560 L 569.86510,90.055570 L 623.86510,90.055570 z M 515.86510,315.05560 L 515.86510,468.05560 L 281.86510,468.05560 L 281.86510,315.05560 L 515.86510,315.05560 z M 623.86510,657.05560 L 623.86510,693.05560 L 173.86510,693.05560 L 173.86510,657.05560 L 623.86510,657.05560 z M 515.86510,531.05560 L 596.86510,603.05560 L 200.86510,603.05560 L 281.86510,531.05560 L 515.86510,531.05560 z ",
        BISHOP: "M 404.23410,59.693330 C 422.23410,59.693330 431.23410,68.693330 431.23410,86.693330 C 431.23410,104.69330 422.23410,113.69330 404.23410,113.69330 C 386.23410,113.69330 377.23410,104.69330 377.23410,86.693330 C 377.23410,68.693330 386.23410,59.693330 404.23410,59.693330 z M 404.23410,167.69330 C 440.23410,221.69330 458.23410,221.69330 503.23410,257.69330 C 548.23410,293.69330 557.23410,338.69330 557.23410,374.69430 C 557.23410,410.69330 536.23410,432.29530 512.23410,446.69430 C 512.23410,446.69430 476.23410,428.69430 404.23410,428.69430 C 332.23410,428.69430 296.23410,446.69430 296.23410,446.69430 C 296.23410,446.69430 251.23410,410.69330 251.23410,374.69430 C 251.23410,338.69330 260.23410,293.69330 305.23410,257.69330 C 350.23410,221.69330 368.23410,221.69330 404.23410,167.69330 z M 503.23410,482.69430 L 512.23410,509.69430 C 467.23410,491.69430 341.23410,491.69430 296.23410,509.69430 L 305.23410,482.69430 C 341.23410,464.69430 467.23410,464.69430 503.23410,482.69430 z M 404.23410,536.69430 C 440.23410,536.69530 494.23410,545.69430 494.23410,545.69430 C 494.23410,545.69430 440.23410,554.69430 404.23410,554.69430 C 368.23410,554.69430 314.23410,545.69530 314.23410,545.69530 C 314.23410,545.69530 368.23410,536.69330 404.23410,536.69430 z M 440.23410,635.69430 C 494.23410,671.69430 503.59610,666.60330 539.23410,671.69430 C 602.23410,680.69430 628.16110,676.01530 656.23410,680.69430 C 710.23410,689.69430 737.23410,698.69430 737.23410,698.69430 L 719.23410,743.69430 C 719.23410,743.69430 710.66410,732.18430 665.23410,725.69430 C 602.23410,716.69430 548.23410,716.69430 503.23410,707.69430 C 458.23410,698.69430 422.23410,680.69430 404.23410,662.69430 C 386.84810,680.08030 350.23410,698.69430 305.23410,707.69430 C 260.23410,716.69430 207.48310,712.84430 143.23410,725.69430 C 98.234040,734.69430 89.234040,743.69430 89.234040,743.69430 L 71.234040,698.69430 C 71.234040,698.69430 98.234040,689.69430 152.23410,680.69430 C 176.77810,676.60330 206.23410,680.69430 269.23410,671.69430 C 305.96910,666.44630 314.23410,671.69430 368.23410,635.69430 L 440.23410,635.69430 z M 431.23410,266.69430 L 377.23410,266.69430 L 377.23410,302.69430 L 341.23410,302.69430 L 341.23410,356.69430 L 377.23410,356.69430 L 377.23410,392.69430 L 431.23410,392.69430 L 431.23410,356.69430 L 467.23410,356.69430 L 467.23410,302.69430 L 431.23410,302.69430 L 431.23410,266.69430 z M 800.23410,653.69430 C 800.23410,653.69430 755.23410,635.69430 692.23410,626.69430 C 655.49910,621.44630 602.23410,635.69430 557.23410,626.69430 C 521.23410,617.69430 485.23410,599.69430 485.23410,599.69430 L 575.23410,554.69430 L 548.23410,473.69430 C 548.23410,473.69430 611.23410,446.69430 611.23410,365.69430 C 611.23410,302.69430 566.23410,230.69430 503.23410,194.69430 C 457.67010,168.65830 449.23410,149.69430 449.23410,149.69430 C 449.23410,149.69430 485.23410,131.69430 485.23410,86.694330 C 485.23410,50.694330 458.23410,5.6943260 404.23410,5.6943260 C 350.23410,5.6943260 323.23410,50.694330 323.23410,86.694330 C 323.23410,131.69430 359.23410,149.69430 359.23410,149.69430 C 359.23410,149.69430 350.79810,168.65830 305.23410,194.69430 C 242.23410,230.69430 197.23410,302.69430 197.23410,365.69430 C 197.23410,446.69430 260.23410,473.69430 260.23410,473.69430 L 233.23410,554.69430 L 323.23410,599.69430 C 323.23410,599.69430 287.23410,617.69430 251.23410,626.69430 C 206.71310,637.82430 149.53510,621.93730 116.23410,626.69430 C 53.234040,635.69430 8.2340370,653.69430 8.2340370,653.69430 L 53.234040,797.69430 C 116.23410,779.69430 125.23410,779.69430 179.23410,770.69430 C 212.32610,765.17930 294.05010,774.42230 332.23410,761.69430 C 386.23410,743.69430 404.23410,716.69430 404.23410,716.69430 C 404.23410,716.69430 422.23410,743.69430 476.23410,761.69430 C 514.41810,774.42230 600.94710,767.15830 629.23410,770.69430 C 683.55610,777.48430 755.23410,797.69430 755.23410,797.69430 L 800.23410,653.69430 L 800.23410,653.69430 z ",
        KNIGHT: "M 76.688770,727.94590 L 556.66680,726.94590 C 556.35380,598.04990 470.35380,554.04990 477.38380,475.20990 L 579.43880,550.04990 C 620.25980,599.03590 666.52580,603.11790 681.49380,574.54390 C 715.51280,581.34690 746.80780,554.13390 745.44780,499.70390 C 744.08780,445.27390 682.85280,364.99090 659.72080,264.29690 C 633.86680,158.15990 604.29080,144.55290 587.96280,139.10890 L 587.60180,61.545870 L 505.95780,121.41890 L 459.69280,41.135870 L 413.42780,136.38790 C 252.86280,88.761870 82.131770,425.86390 76.688770,727.94590 z M 505.95780,677.95990 L 126.31380,677.95990 C 205.68580,187.71690 362.68580,154.71690 437.92180,193.53890 L 462.41480,144.55290 L 481.46480,178.57090 L 567.19080,198.98090 L 576.71580,189.45790 C 597.12680,205.78590 608.14980,284.03590 634.35280,350.71790 C 662.29280,421.82190 697.90980,477.31990 697.82080,496.98190 C 697.68580,526.71790 689.01880,532.71790 671.96680,525.55790 C 663.68580,512.04990 655.01880,500.71790 639.30980,499.70390 C 632.35280,500.04990 621.14380,503.00890 631.68580,509.71790 C 646.35280,519.04990 642.75180,540.16490 642.75180,540.16490 C 616.01880,518.71790 515.25280,437.01890 459.69280,401.73090 C 442.35180,390.71690 426.68480,380.71690 414.68480,350.21690 C 390.82180,377.37090 416.35180,430.71690 431.68480,444.04890 C 408.35180,536.04890 484.35180,618.71690 505.95680,677.95890 L 505.95780,677.95990 z M 682.04780,490.00990 C 682.04780,485.18590 675.98380,472.91790 669.91880,467.95690 C 663.85480,462.99390 654.48180,460.23590 648.96880,460.37490 C 643.45580,460.51390 634.49680,465.74990 634.90980,472.36690 C 635.32280,478.98190 647.17680,480.77490 651.86280,482.56590 C 656.54880,484.35690 662.88880,496.62590 669.50480,500.75990 C 676.12080,504.89390 682.04780,496.67790 682.04780,490.00990 L 682.04780,490.00990 z M 588.45680,320.97290 C 588.11380,280.48690 578.16380,263.67390 566.49780,249.26390 C 554.83180,234.85190 512.97280,215.29490 512.97280,215.29490 C 512.97280,215.29490 508.16880,266.41790 525.66780,296.26990 C 543.16680,326.11990 570.61480,321.31690 588.45680,320.97290 L 588.45680,320.97290 z ",
        PAWN: "M 688.02380,753.51590 L 688.02380,627.51590 C 688.02380,582.51590 661.62380,455.01590 553.02380,411.51590 C 598.02380,357.51590 607.02380,258.51590 517.02380,195.51590 C 544.02380,159.51590 517.02380,33.515900 409.02380,33.515900 C 301.02380,33.515900 274.02380,159.51590 301.02380,195.51590 C 211.02380,258.51590 220.02380,357.51590 265.02380,411.51590 C 157.02380,456.51590 130.02380,582.51590 130.02380,627.51590 L 130.02380,753.51590 L 688.02380,753.51590 z M 409.02380,87.515900 C 490.02380,87.515900 490.02380,177.51590 454.02380,213.51590 C 562.02380,258.51590 535.02380,375.51590 481.02380,429.51590 C 571.02380,456.51590 634.02380,546.51590 634.02380,609.51590 L 634.02380,699.51590 L 184.02380,699.51590 L 184.02380,609.51590 C 184.02380,546.51590 247.02380,456.51590 337.02380,429.51590 C 283.02380,375.51590 256.02380,258.51590 364.02380,213.51590 C 328.02380,177.51590 328.02380,87.515900 409.02380,87.515900 z "
    }
}

parsedPieces = [[[], [], [], [], [], [], []], \
                [[], [], [], [], [], [], []]]
for color in (WHITE, BLACK):
    for piece in range(PAWN, KING+1):
        list = []
        thep = [0,0]
        for g1, g2 in elemExpr.findall(pieces[color][piece]):
            if not g1 or not g2: continue
            points = [float(s) for s in spaceExpr.split(g2)]
            list += [(g1, [f-thep[i%2] for i,f in enumerate(points)])]
            thep = points[-2:]
        parsedPieces[color][piece] = {size:list}
