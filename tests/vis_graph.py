from graphviz import Digraph  # type: ignore

dot = Digraph(comment='The Round Table')

dot.node('A', 'King Arthur')
dot.node('B', 'Sir Bedevere the Wise')
dot.node('L', 'Sir Lancelot the Brave')

dot.edges(['AB', 'AL'])
dot.edge('B', 'L', constraint='false')

print(dot.source)  # 输出 DOT 语言描述的图
dot.render('round-table.gv', view=True) # 生成图像并显示