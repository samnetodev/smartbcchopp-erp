import { Package, PackageOpen, AlertTriangle } from 'lucide-react'

interface Props {
  total_produtos: number
  total_itens_estoque: number
  estoque_baixo: number
}

export default function EstoqueWidget({ total_produtos, total_itens_estoque, estoque_baixo }: Props) {
  return (
    <div className="card p-5">
      <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <Package className="w-4 h-4 text-violet-500" />
        Estoque
      </h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-2xl font-bold text-gray-900">{total_produtos}</p>
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <PackageOpen className="w-3 h-3" /> Produtos
          </p>
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{total_itens_estoque}</p>
          <p className="text-xs text-gray-500">Itens em estoque</p>
        </div>
        {estoque_baixo > 0 && (
          <div className="col-span-2">
            <div className="flex items-center gap-2 p-3 rounded-lg bg-rose-50">
              <AlertTriangle className="w-4 h-4 text-rose-600" />
              <div>
                <p className="text-sm font-medium text-rose-600">{estoque_baixo} produtos</p>
                <p className="text-xs text-rose-500">com estoque abaixo do mínimo</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
