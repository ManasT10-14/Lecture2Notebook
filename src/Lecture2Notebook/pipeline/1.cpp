#include <bits/stdc++.h>
using namespace std;

int main() {

    int n1;
    cin >> n1;
    vector<double> B(2*n1+1);
    for(int i=0;i<=2*n1;i++) cin >> B[i];

    nth_element(B.begin(), B.begin()+n1, B.end());

    vector<double> A(2*n1+1);
    int l=0,r=n1+1;
    for(int i=0;i<=2*n1;i++){
        if(i%2==0) A[i]=B[l++];
        else A[i]=B[r++];
    }

    for(double x:A) cout<<x<<" ";
    cout<<"\n";

    int n2;
    cin >> n2;
    vector<int> S(n2);
    for(int i=0;i<n2;i++) cin >> S[i];
    int x;
    cin >> x;

    int i=0,j=n2-1;
    bool found=false;
    while(i<j){
        if(S[i]+S[j]==x){
            found=true;
            break;
        }
        else if(S[i]+S[j]<x) i++;
        else j--;
    }

    cout<<(found?"YES":"NO")<<"\n";

    int n3;
    cin >> n3;
    vector<int> bin(n3);
    for(int i=0;i<n3;i++) cin >> bin[i];

    int c0=0;
    for(int i=0;i<n3;i++) if(bin[i]==0) c0++;

    for(int i=0;i<c0;i++) cout<<0<<" ";
    for(int i=c0;i<n3;i++) cout<<1<<" ";

    return 0;
}
