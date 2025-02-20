import pwndbg.color.message as message
import pwndbg.config
import pwndbg.heap.heap
import pwndbg.symbol

current = None

main_arena = pwndbg.config.Parameter("main_arena", "0", "main_arena address for heuristics", "heap")

thread_arena = pwndbg.config.Parameter(
    "thread_arena", "0", "thread_arena value for heuristics", "heap"
)

mp_ = pwndbg.config.Parameter("mp_", "0", "mp_ address for heuristics", "heap")

tcache = pwndbg.config.Parameter("tcache", "0", "tcache value for heuristics", "heap")

global_max_fast = pwndbg.config.Parameter(
    "global_max_fast", "0", "global_max_fast address for heuristics", "heap"
)

symbol_list = pwndbg.config.get_params("heap")

heap_chain_limit = pwndbg.config.Parameter(
    "heap-dereference-limit", 8, "number of bins to dereference", "heap"
)

resolve_heap_via_heuristic = pwndbg.config.Parameter(
    "resolve-heap-via-heuristic",
    False,
    "Resolve missing heap related symbols via heuristics",
    "heap",
)


@pwndbg.events.start
def update():
    resolve_heap(is_first_run=True)


@pwndbg.events.stop
@pwndbg.events.new_objfile
def reset():
    global current
    # Re-initialize the heap
    if current:
        current = type(current)()
    for symbol in symbol_list:
        symbol.value = "0"


@pwndbg.config.Trigger([resolve_heap_via_heuristic])
def resolve_heap(is_first_run=False):
    import pwndbg.heap.ptmalloc

    global current
    if resolve_heap_via_heuristic:
        current = pwndbg.heap.ptmalloc.HeuristicHeap()
        if not is_first_run and pwndbg.proc.alive and current.libc_has_debug_syms():
            print(
                message.warn(
                    "You are going to resolve the heap via heuristic even though you have libc debug symbols."
                    " This is not recommended!"
                )
            )
        else:
            print(
                message.warn(
                    "You are going to resolve the heap via heuristic. This might not work in all cases."
                )
            )
    else:
        current = pwndbg.heap.ptmalloc.DebugSymsHeap()
