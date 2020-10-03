#!/usr/bin/env python
# coding: utf-8

# __Задача #15 (5.2)__
# 
# Реализовать компьютерную симуляцию модели SIR:
# 
# * Логика модели:
#     * каждый узел находится в одном из трех состояний $\{ S, I, R\}$
#     * на 0-м шаге $c$ узлов устанавливаются в состояние $I$ (остальные - в $S$)
#     * На каждом шаге каждый из инфецированных узлов с вероятностю $\beta$ заражает каждый из связанных с ним уязвимых узлов
#     * Каждый инфецированный узел остается инфецированным $\tau_\gamma =1/\gamma$ временных шагов, после чего переходит в состояние $R$ и не может быть вновь инфецированным. Кроме того узлы в состоянии $R$ не распространяют инфекцию.
# 
# * Модификация модели: 10% узлов с максимальной степенью центральности изолируются т.е. имеют $\beta'=\beta/2$
# 
# Сравнить симуляции динамики заражения узлов (в виде графиков динамики уязвимых, зраженных и резистентных узлов) сети модели для социальных сетей (не менее 3х) с несколькими тысячами узлов в 5 вариантах (все 5 вариантов на одном графике):
# * базовая модель
# * модифицированная модель (степень центральности - по степени)
# * модифицированная модель (степень центральности - по близости)
# * модифицированная модель (степень центральности - по посредничеству)
# * модифицированная модель (степень центральности - по собственному значению)
# 
# Интерпретировать полученный результат.

# In[2]:


import networkx as nx
import matplotlib.pyplot as plt
import random 
import numpy as np


# # Базовая модель

# In[3]:


#проверка моделей будет осуществляться на карате клубе
G = nx.karate_club_graph()

nx.draw(G,node_color='deepskyblue',with_labels=True,node_size=500)
plt.show()


# In[4]:


#задаем параметры
beta=0.5
gamma=0.5
t=15 #кол-во шагов
c=5 #кол-во первых заражений
teta=int(1/gamma)
teta


# In[5]:


#функция для базовой модели которая возвращает словарь состоящий из списка состояний модели от шага к шагу
def bazovaya(G):
    ed=list(G.edges)
    l=list(G.nodes)
    d = {a: [] for a in range(t+1)}
    
    #формируем нулевой шаг засчет случайного выбора 5 узлов, которые будут заражены
    f=random.sample(G.nodes,5)
    p=[]
    for i in range(len(l)):
        m_key=i in f
        if m_key==True:
            p.append('I')
        else:
            p.append('S')
    d[0]=p
    
#формируем шаги с первого по последний, проходясь по словарю и меняя начальные значения узлов S 
    k=0
    while k<t:
        k=k+1
        p=d[k-1]
        p1=list(p)
        
#если в предыдущем шаге значение узла было I тогда проходимся по всем связям этого узла
#если оно не было равно R тогда записываем этот узел в список p, после чего рандомно выбираем из него 50% 
#узлов которые будут заражены дополнительно в этом шаге
        for n in range(len(p)):
            if p[n]=='I':
                t1=[]
                for j in range(len(ed)):
                    y=ed[j]
                    if y[0]==n:
                        if p[y[1]]!='R':
                            t1.append(y[1])
                    if y[1]==n:
                        if p[y[0]]!='R':
                            t1.append(y[0])
                m1=len(t1)*beta
                m=round(m1,0)
                newd = random.sample(t1,int(m))
                    #print(newd)

                for i in range(len(p1)):
                    m_key=i in newd
                    if m_key==True:
                        p1[i]='I'
            d[k]=p1
#если шаг становится больше чем тета, начинают появляться R, которые уже не смогут заразиться
#R появляются из зараженных за шаг который был тета шагов назад
        if k>teta:
            e1=d[k-teta-1]
            e2=d[k]
            for i in range(len(e2)):
                if e1[i]=='I':
                    e2[i]='R'
            d[k]=e2
    return d


d=bazovaya(G)


# In[6]:


#посмотрим как выглядит модель пошагово и в динамике
colors = {a: [] for a in range(t+1)}
Sx= [0 for a in range(t+1)]
Ix= [0 for a in range(t+1)]
Rx= [0 for a in range(t+1)]

for n in range(len(d)):
    p=list(d[n])
    k=colors[n]
    for i in range(len(p)):
        if p[i]=='I':
            Ix[n]=Ix[n]+1
            k.append('r')
        else:
            if p[i]=='R':
                k.append('limegreen')
                Rx[n]=Rx[n]+1
            else:
                k.append('deepskyblue')
                Sx[n]=Sx[n]+1


# In[7]:


#пошагово для карате клуба
t=8
for i in range(len(d)):
    nx.draw(G,node_color=colors[i],with_labels=True,node_size=500)
    plt.show()


# In[8]:


#динамика
plt.plot(Sx,color='deepskyblue')
plt.plot(Ix,color='r')
plt.plot(Rx,color='limegreen')


# # Модифицированная модель

# ### степень центральности - по степени

# In[9]:


#задаем параметры
beta=0.5
gamma=0.7
t=15
teta=int(1/gamma)
degR=0.1
beta_deg=beta/2
ed=list(G.edges)
l=list(G.nodes)


# In[10]:


#посчитаем степени центральности для сети

deg_cent = nx.degree_centrality(G)

def spisok(deg):
    degL = list(deg.items())
    degL.sort(key=lambda i: i[1],reverse=True)
    spisok=[]

    #возьмем 10% узлов с максимальной степенью центральности и добавим их в список
    lin=int(round(len(degL)*degR,0))
    for i in range(lin):
        ni=degL[i]
        spisok.append(ni[0])
    return spisok


# In[11]:


#задаем веса для каждого из узлов, 
#для узлов из списка deg_spisok это бета/2, остальные - бета

def weig(spisok,G):
    l=list(G.nodes)
    weights1=[0 for a in range(len(l))]
    
    for i in range(len(l)):
        tre=i in spisok
        if tre==True:
            weights1[i]=beta/2
        else:
            weights1[i]=beta
    return weights1


# In[12]:


#функция для модифицированной модели где все то же самое только с весами
def moddeg(weights1,G,f):
    d = {a: [] for a in range(t+1)}
    ed=list(G.edges)
    l=list(G.nodes)
    p=[]
    for i in range(len(l)):
        m_key=i in f
        if m_key==True:
            p.append('I')
        else:
            p.append('S')
    d[0]=p

    k=0
    while k<t:
        k=k+1
        p=d[k-1]
        p1=list(p)
        for n in range(len(p)):
            if p[n]=='I':
                t1=[]
                w=[]
                m1=0
                for j in range(len(ed)):
                    y=ed[j]
                    if y[0]==n:
                        if p[y[1]]!='R':
                            t1.append(y[1])
                            se=y[1]
                            w.append(weights1[se])
                    if y[1]==n:
                        if p[y[0]]!='R':
                            t1.append(y[0])
                            se=y[0]
                            #print(se)
                            w.append(weights1[se])
               
                for sos in range(len(w)):
                    m1=m1+w[sos]
                m=round(m1,0)
                if len(t1)!=0:
                    newd = random.choices(population=t1,weights=w,k=int(m))
                    #print(newd)

                for i in range(len(p1)):
                    m_key=i in newd
                    if m_key==True:
                        p1[i]='I'
            d[k]=p1
        if k>teta:
            e1=d[k-teta-1]
            e2=d[k]
            for i in range(len(e2)):
                if e1[i]=='I':
                    e2[i]='R'
            d[k]=e2
    return d


# In[13]:


colors = {a: [] for a in range(5)}


def col(d,whomst):
    Sx= [0 for a in range(t+1)]
    Ix= [0 for a in range(t+1)]
    Rx= [0 for a in range(t+1)]
    for n in range(len(d)):
        p=list(d[n])
        for i in range(len(p)):
            if p[i]=='I':
                Ix[n]=Ix[n]+1
            else:
                if p[i]=='R':
                    Rx[n]=Rx[n]+1
                else:
                    Sx[n]=Sx[n]+1
    l[1]=Ix
    l[2]=Rx
    l[3]=Sx
    colors[whomst]=l
    return colors


# In[14]:


model=['base','deg','clo','bet','mine']
def ris(who):
    intro=colors[who]
    #plt.title(model[who])
    plt.plot(intro[3],color='deepskyblue')
    plt.plot(intro[1],color='r')
    plt.plot(intro[2],color='limegreen')

def deg(G):
    l=list(G.nodes)
    deg_cent = nx.degree_centrality(G)
    sp = spisok(deg_cent)
    weigh=weig(sp,G)
    f_deg=random.choices(l,weights=weigh,k=5)
    d_degmax=moddeg(weigh,G,f_deg)
    colors=col(d_degmax,1)    
    ris(1)
    
deg(G)


# ### степень центральности - по близости

# In[15]:


def clo(G):
    l=list(G.nodes)
    bet_cent=nx.betweenness_centrality(G) 
    bet_spisok=spisok(bet_cent)
    weigh_bet=weig(bet_spisok,G)
    f_med=random.choices(l,weights=weigh_bet,k=5)
    d_med=moddeg(weigh_bet,G,f_med)
    colors=col(d_med,2)
    ris(2)

clo(G)


# ### степень центральности - по посредничеству

# In[16]:


def bet(G):
    l=list(G.nodes)
    bet_cent=nx.betweenness_centrality(G) 
    bet_spisok=spisok(bet_cent)
    weigh_bet=weig(bet_spisok,G)
    f_med=random.choices(l,weights=weigh_bet,k=5)
    d_med=moddeg(weigh_bet,G,f_med)
    colors=col(d_med,3)
    ris(3)

bet(G)


# ### степень центральности - по собственному значению (влиятельность)

# In[17]:


def my(G):
    l=list(G.nodes)
    
    my_cent=nx.eigenvector_centrality_numpy(G) 
    
    my_spisok=spisok(my_cent)
    weigh_my=weig(my_spisok,G)
    f_my=random.choices(l,weights=weigh_my,k=5)
    d_my=moddeg(weigh_my,G,f_my)
    colors=col(d_my,4)
    ris(4)

my(G)


# # модели соц сетей

# In[18]:


t=15
G_pervoe = nx.newman_watts_strogatz_graph(2000,5,3)


# In[19]:


def base(G):
    l=list(G.nodes)
    d=bazovaya(G)
    colors=col(d,0)
    ris(0)
base(G_pervoe)
bet(G_pervoe)
clo(G_pervoe)
deg(G_pervoe)
my(G_pervoe)


# In[20]:


G_vtoroe = nx.barabasi_albert_graph(1512,3)
base(G_vtoroe)
bet(G_vtoroe)
clo(G_vtoroe)
deg(G_vtoroe)
my(G_vtoroe)


# In[21]:


G_tri = nx.connected_caveman_graph(1,1042)
base(G_tri)
bet(G_tri)
clo(G_tri)
deg(G_tri)
my(G_tri)


# ## Вывод: 
# ### Без модификаций заразится больше узлов, прежде чем количество зараженных начнет падать, значит и потребуется больше времени на вылечивание. Для различных степеней центральности результаты по модификациям практически одинаковы

# In[ ]:




