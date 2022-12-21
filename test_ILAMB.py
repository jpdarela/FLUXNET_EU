# test_ILAMB.py
import matplotlib.pyplot as plt
from ILAMB.Variable import Variable
from ILAMB import ilamblib as il


def plot(obs,mod,title="Comp"): 
    fig, axs = plt.subplots(1,1)
    obs.plot(ax=axs, color="k")
    mod.plot(ax=axs, color="g")
    plt.legend(["obs","mod"])
    plt.savefig(f"{title}.png")
    plt.clf()
    plt.close(fig)
    
    
obs = Variable(filename="reco_BK1_FLUXNET2015.nc", variable_name="reco")
mod = Variable(filename="reco_Hai_FLUXNET2015.nc", variable_name="reco")

print(obs)
print(mod)
plot(obs,mod, "before_conform")

# Make comparable
obs1, mod1 = il.MakeComparable(obs, mod, clip_ref=True)

plot(obs1,mod1, "after_conform")

# How much carbon was respired in the matching period
# Temporal integration of the FLUX
obs_acc = obs1.accumulateInTime().convert("Mg ha-1")
mod_acc = mod1.accumulateInTime().convert("Mg ha-1")

plot(obs_acc, mod=mod_acc, title="cumulative_resp")

bias = obs1.bias(mod1)
print(bias)

rmse = obs1.rmse(mod1)
print(rmse)

